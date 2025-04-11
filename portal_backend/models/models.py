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
    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(null=True, default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    approved_ap_details = models.JSONField(null=True)
    published_ap_details = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization.name_en

    @property
    def new_ap_details(self):
        ap_scheme_entry = {
            "id": self.id,
            "name": {"en": self.organization.name_en, "nl": self.organization.name_nl},
            "shortname": {"en": self.shortname_en, "nl": self.shortname_nl},
            "logo": (
                self.organization.logo.url
                if self.organization.logo and self.organization.logo.name
                else None
            ),
            "base_url": self.base_url,
            "scheme": self.yivi_tme.environment,
        }
        return ap_scheme_entry

    @property
    def status(self) -> str:
        if self.reviewed_accepted is True and self.published_at:
            return StatusChoices.PUBLISHED
        if self.reviewed_accepted is True:
            return StatusChoices.ACCEPTED
        if self.reviewed_accepted is False:
            return StatusChoices.REJECTED
        if self.ready:
            return StatusChoices.PENDING_FOR_REVIEW
        return StatusChoices.DRAFT

    def save(self, *args, **kwargs):
        if self.ready and not self.ready_at:
            self.ready_at = timezone.now()
        elif not self.ready:
            self.ready_at = None
            self.reviewed_accepted = None
            self.reviewed_at = None
            self.rejection_remarks = None
            self.published_at = None

        previous = (
            AttestationProvider.objects.filter(pk=self.pk).first() if self.pk else None
        )

        if previous and not previous.reviewed_accepted and self.reviewed_accepted:
            self.approved_ap_details = self.new_ap_details
            self.reviewed_at = timezone.now()
        elif not previous and self.reviewed_accepted:
            self.approved_ap_details = self.new_ap_details
            self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)


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
    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(null=True, default=None)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    approved_rp_details = models.JSONField(null=True, default=None, blank=True)
    published_rp_details = models.JSONField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name_en}"

    @property
    def rp_details(self):
        hostname = RelyingPartyHostname.objects.filter(relying_party=self).first()
        requestor_scheme_entry = {
            "id": self.id,
            "name": {"en": self.organization.name_en, "nl": self.organization.name_nl},
            "logo": (
                self.organization.logo.url
                if self.organization.logo and self.organization.logo.name
                else None
            ),
            "hostnames": [hostname.hostname],
            "scheme": self.yivi_tme.environment,
        }
        return requestor_scheme_entry

    @property
    def status(self) -> str:
        if self.reviewed_accepted is True and self.published_at:
            return StatusChoices.PUBLISHED
        if self.reviewed_accepted is True:
            return StatusChoices.ACCEPTED
        if self.reviewed_accepted is False:
            return StatusChoices.REJECTED
        if self.ready:
            return StatusChoices.PENDING_FOR_REVIEW
        return StatusChoices.DRAFT

    def save(self, *args, skip_import_approve=False, **kwargs):
        if self.ready and not self.ready_at:
            self.ready_at = timezone.now()
        elif not self.ready:
            self.ready_at = None
            self.reviewed_accepted = None
            self.reviewed_at = None
            self.rejection_remarks = None
            self.published_at = None

        previous = RelyingParty.objects.filter(pk=self.pk).first() if self.pk else None

        if previous and not previous.reviewed_accepted and self.reviewed_accepted:
            self.approved_rp_details = self.rp_details
            self.reviewed_at = timezone.now()
        elif not previous and self.reviewed_accepted:
            self.approved_rp_details = self.rp_details
            self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)


class StatusChoices(models.TextChoices):
    """Choices for the status of a Relying Party or Attestation Provider."""

    DRAFT = "draft", "Draft"
    PENDING_FOR_REVIEW = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    PUBLISHED = "published", "Published"
    # the ap or rp became invalid after being published, possibly due to a failure in dns_challenge  (for the rp)
    INVALIDATED = "invalidated", "Invalidated"


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
