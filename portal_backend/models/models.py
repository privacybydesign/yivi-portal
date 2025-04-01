from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import URLValidator, RegexValidator, FileExtensionValidator
from django.core.files.storage import FileSystemStorage
import uuid
import os
import hashlib
from imagekit.models import ProcessedImageField  # type: ignore
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class LogoStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            # If the file already exists, delete it, because we want to overwrite it
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

    @staticmethod
    def hash_file_contents(file_contents):
        sha256 = hashlib.sha256()
        sha256.update(file_contents)
        return sha256.hexdigest()

    @staticmethod
    def get_logo_path(instance, filename):
        """Determine the path for a logo image, based on the contents of the file"""
        instance.logo.file.seek(0)
        content_hash = LogoStorage.hash_file_contents(instance.logo.file.read())
        filename, file_extension = os.path.splitext(filename)
        return f"{content_hash}{file_extension}"


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    contact_address = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True)
    trade_names = models.JSONField(default=list)
    logo = ProcessedImageField(
        upload_to=LogoStorage.get_logo_path,
        storage=LogoStorage(),
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"])],
    )
    approved_logo = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    trust_model = models.ForeignKey(
        "TrustModel",
        on_delete=models.CASCADE,
        related_name="organizations",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name_en

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logo = self.logo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        # If the logo has changed when saving, delete the old one
        # But only if it's not the same as the approved logo, since we keep a copy of all logos that have ever been approved.
        if self._logo != self.logo and self._logo:
            if not self.approved_logo == self._logo:
                self.logo.storage.delete(self._logo.path)

        return super().save(*args, **kwargs)

    # When deleting an organization, delete all associated logos
    def delete(self, *args, **kwargs):
        if self.logo:
            storage, path = self.logo.storage, self.logo.path
            storage.delete(path)

        if self.approved_logo:
            storage, path = self.approved_logo.storage, self.approved_logo.path
            storage.delete(path)

        super().delete(*args, **kwargs)

    @property
    def is_RP(self):
        return RelyingParty.objects.filter(organization=self).exists()

    @property
    def is_AP(self):
        return AttestationProvider.objects.filter(organization=self).exists()


class TrustModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    eudi_compliant = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class YiviTrustModelEnv(models.Model):
    ENV_CHOICES = [
        ("production", "Production"),
        ("development", "Development"),
        ("demo", "Demo"),
    ]
    trust_model = models.ForeignKey(
        TrustModel, on_delete=models.CASCADE, related_name="environments"
    )
    environment = models.CharField(max_length=50, choices=ENV_CHOICES)
    timestamp_server = models.CharField(max_length=255)
    keyshare_server = models.CharField(max_length=255)
    keyshare_website = models.CharField(max_length=255)
    keyshare_attribute = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    minimum_android_version = models.CharField(max_length=20)
    minimum_ios_version = models.CharField(max_length=20)
    description_en = models.TextField()
    description_nl = models.TextField()
    url = models.URLField(validators=[URLValidator()])

    def __str__(self):
        return f"{self.trust_model.name} - {self.environment}"


class AttestationProvider(models.Model):
    yivi_tme = models.ForeignKey(
        YiviTrustModelEnv,
        on_delete=models.CASCADE,
        related_name="attestation_providers",
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="attestation_providers"
    )
    version = models.CharField(max_length=50)
    shortname_en = models.CharField(max_length=100, null=True, blank=True)
    shortname_nl = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(max_length=255, null=True, blank=True)
    base_url = models.URLField(null=True, blank=True)
    # what will be added to issuers scheme
    approved_ap_details = models.JSONField(null=True)
    published_ap_details = models.JSONField(null=True)  # what is actually published
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization.name_en

    @property
    def new_ap_details(self):
        requestor_scheme_entry = {
            "id": self.id,
            "name": {"en": self.organization.name_en, "nl": self.organization.name_nl},
            "shortname": {"en": self.shortname_en, "nl": self.shortname_nl},
            "logo": self.organization.logo.url,  # will need to be the hash of the logo
            "base_url": self.base_url,
            "scheme": self.yivi_tme.environment,
        }
        return requestor_scheme_entry

    @property
    def published(self):
        pass


class RelyingParty(models.Model):
    class Meta:
        verbose_name = "Relying Party"
        verbose_name_plural = "Relying Parties"

    rp_slug = models.SlugField(unique=True, null=True, blank=True)
    yivi_tme = models.ForeignKey(
        YiviTrustModelEnv, on_delete=models.CASCADE, related_name="relying_parties"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="relying_parties"
    )
    # what will be added to requestors scheme (formerly called scheme data)
    approved_rp_details = models.JSONField(null=True, default=None, blank=True)
    published_rp_details = models.JSONField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name_en}"

    @property
    def new_rp_details(self):
        hostname = RelyingPartyHostname.objects.filter(relying_party=self).first()
        requestor_scheme_entry = {
            "id": self.id,
            "name": {"en": self.organization.name_en, "nl": self.organization.name_nl},
            "logo": self.organization.logo.url,  # will need to be the hash of the logo
            # right now the verifier can only have one hostname
            "hostnames": [hostname.hostname],
            "scheme": self.yivi_tme.environment,
        }
        return requestor_scheme_entry

    # construct new rp details based on RP hostname , condiscon and rest of needed data

    def approve(self):
        if not self.status.ready:
            raise ValidationError(
                "Relying Party must be marked as ready before approving."
            )

        self.approved_rp_details = self.new_rp_details
        self.status.reviewed_accepted = True
        self.status.reviewed_at = timezone.now()

    @property
    def published(self):
        # check requestors json and see if the rp with approved_rp_details is in there
        pass


class StatusChoices(models.TextChoices):
    """Choices for the status of a Relying Party or Attestation Provider."""

    DRAFT = "draft", "Draft"
    PENDING_FOR_REVIEW = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    PUBLISHED = "published", "Published"
    # the ap or rp became invalid after being published, possibly due to a failure in dns_challenge  (for the rp)
    INVALIDATED = "invalidated", "Invalidated"


class Status(models.Model):
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        constraints = [
            CheckConstraint(
                check=Q(relying_party__isnull=False, attestation_provider__isnull=True)
                | Q(relying_party__isnull=True, attestation_provider__isnull=False),
                name="either_rp_or_ap",
            )
        ]

    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(null=True, default=None)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    relying_party = models.OneToOneField(
        RelyingParty,
        on_delete=models.CASCADE,
        related_name="status",
        null=True,
        blank=True,
    )
    attestation_provider = models.OneToOneField(
        AttestationProvider,
        on_delete=models.CASCADE,
        related_name="status",
        null=True,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_ready = self.ready
        self._initial_reviewed_accepted = self.reviewed_accepted
        self._initial_rejection_remarks = None

    def clean(self):
        if self.ready:
            if self.relying_party:
                has_hostname = RelyingPartyHostname.objects.filter(
                    relying_party=self.relying_party
                ).exists()
                if not has_hostname:
                    raise ValidationError(
                        "No hostname specified for the Relying Party."
                    )

                has_condiscon = Condiscon.objects.filter(
                    relying_party=self.relying_party
                ).exists()
                if not has_condiscon:
                    raise ValidationError(
                        "No condiscon specified for the Relying Party."
                    )

            elif self.attestation_provider:
                pass

    def save(self, *args, **kwargs):
        if self.ready and not self._initial_ready:
            self.ready_at = timezone.now()
        elif self._initial_ready and not self.ready:  # marked as draft again
            self.ready_at = None
            self.reviewed_accepted = None
            self.reviewed_at = None
            self.rejection_remarks = None
            self.published_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.relying_party:
            entity_name = self.relying_party.organization.name_en
        elif self.attestation_provider:
            entity_name = self.attestation_provider.organization.name_en
        else:
            entity_name = "Unknown"

        return f"Status {entity_name} - Ready: {self.ready}"

    @property
    def rp_status(self):
        rphostname = RelyingPartyHostname.objects.filter(
            relying_party=self.relying_party
        ).first()
        if not rphostname:
            return StatusChoices.DRAFT
        # if rp is published and then dns_challenge is invalidated
        elif rphostname and self.relying_party.published and rphostname.invalidated:
            return StatusChoices.INVALIDATED
        elif self.ready and self.relying_party.published:
            return StatusChoices.PUBLISHED
        elif self.reviewed_accepted is False:
            return StatusChoices.REJECTED
        elif self.reviewed_accepted is True:
            return StatusChoices.ACCEPTED
        elif self.ready:
            return StatusChoices.PENDING_FOR_REVIEW
        return StatusChoices.DRAFT

    @property
    def ap_status(self):
        pass


class Credential(models.Model):
    attestation_provider = models.ForeignKey(
        AttestationProvider, on_delete=models.CASCADE, related_name="credentials"
    )
    credential_tag = models.CharField(max_length=100)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    description_en = models.TextField()
    description_nl = models.TextField()

    def __str__(self):
        return self.name_en


class CredentialAttribute(models.Model):
    name = models.CharField(max_length=255)
    credential = models.ForeignKey(
        Credential, on_delete=models.CASCADE, related_name="attributes"
    )

    class Meta:
        unique_together = ("credential", "name")

    def __str__(self):
        return self.name


class RelyingPartyHostname(models.Model):
    DOMAIN_REGEX = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*(\.[A-Za-z]{2,6})+$"
    hostname = models.CharField(
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex=DOMAIN_REGEX,
                message="Enter a valid domain (e.g., example.com).",
                code="invalid_domain",
            )
        ],
    )
    dns_challenge = models.CharField(max_length=255, null=True, blank=True)
    dns_challenge_created_at = models.DateTimeField(null=True, blank=True)
    dns_challenge_verified = models.BooleanField(null=True, blank=True)
    dns_challenge_verified_at = models.DateTimeField(null=True, blank=True)
    dns_challenge_invalidated_at = models.DateTimeField(null=True, blank=True)
    manually_verified = models.BooleanField(null=True, blank=True)
    relying_party = models.ForeignKey(
        RelyingParty, on_delete=models.CASCADE, related_name="hostnames"
    )

    @property
    def invalidated(
        self,
    ):  # TODO if dns_challenge is invalidated or if the published_rp_details is now different than approved_rp_details
        return (
            self.dns_challenge_verified
            and self.dns_challenge_invalidated_at is not None
        )

    def __str__(self):
        return self.hostname


class Condiscon(models.Model):
    condiscon = models.JSONField()
    context_description_en = models.CharField(max_length=255)
    context_description_nl = models.CharField(max_length=255)
    relying_party = models.ForeignKey(
        RelyingParty, on_delete=models.CASCADE, related_name="condiscons"
    )

    def __str__(self):
        return str(self.condiscon)


class CondisconAttribute(models.Model):
    credential_attribute = models.ForeignKey(
        CredentialAttribute,
        on_delete=models.CASCADE,
        related_name="condiscon_attributes",
    )
    condiscon = models.ForeignKey(Condiscon, on_delete=models.CASCADE)
    reason_en = models.TextField()
    reason_nl = models.TextField()

    def __str__(self):
        return f"{self.credential_attribute.credential.name_en}"


class User(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("maintainer", "Maintainer"),
    ]
    email = models.EmailField(max_length=255, unique=True, null=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="users", null=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email} - {self.role}"
