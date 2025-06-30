from django.db import models
from django.db.models import Exists, OuterRef
from django.core.validators import URLValidator, RegexValidator, FileExtensionValidator
from django.core.files.storage import FileSystemStorage
import uuid
import os
import hashlib
from imagekit.models import ProcessedImageField  # type: ignore
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django_countries.fields import CountryField  # type: ignore
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore


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


class OrganizationQuerySet(models.QuerySet):
    def with_role_annotations(self):
        return self.annotate(
            is_rp=Exists(
                RelyingParty.objects.filter(
                    organization=OuterRef("pk"),
                    published=True,
                    organization__is_verified=True,
                )
            ),
            is_ap=Exists(
                AttestationProvider.objects.filter(
                    organization=OuterRef("pk"),
                    published=True,
                    organization__is_verified=True,
                )
            ),
        )


class ConvertToRGB(object):
    def process(self, image):
        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGBA", image.size, (255, 255, 255, 255))
            background.paste(image, (0, 0), image)
            return background.convert("RGB")
        return image.convert("RGB")


class Organization(models.Model):
    objects = OrganizationQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    street = models.CharField(max_length=35, null=True, blank=True)
    house_number = models.CharField(max_length=35, null=True, blank=True)
    contact_number = PhoneNumberField(blank=True, null=True)
    postal_code = models.CharField(max_length=35, null=True, blank=True)
    city = models.CharField(max_length=35, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    logo = ProcessedImageField(
        upload_to=LogoStorage.get_logo_path,
        processors=[ConvertToRGB()],
        storage=LogoStorage(),
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"])],
    )
    approved_logo = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_en

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logo = self.logo
        self._name_en = self.name_en
        self._name_nl = self.name_nl
        self._street = self.street
        self._house_number = self.house_number
        self._postal_code = self.postal_code
        self._city = self.city
        self._country = self.country

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        # If the logo has changed when saving, delete the old one
        # But only if it's not the same as the approved logo, since we keep a copy of all logos that have ever been approved.
        if self._logo != self.logo and self._logo:
            if not self.approved_logo == self._logo:
                self.logo.storage.delete(self._logo.path)
        # if any of the fields changed is_verified resets to False
        if (
            self._logo != self.logo
            or self._name_en != self.name_en
            or self._name_nl != self.name_nl
            or self._street != self.street
            or self._house_number != self.house_number
            or self._postal_code != self.postal_code
            or self._city != self.city
            or self._country != self.country
        ):
            self.is_verified = False

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


class TrustModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    eudi_compliant = models.BooleanField(default=False)
    organizations = models.ManyToManyField("Organization", related_name="trust_models")

    def __str__(self):
        return self.name


class YiviTrustModelEnv(models.Model):
    ENV_CHOICES = [
        ("production", "Production"),
        ("staging", "Staging"),
        ("demo", "Demo"),
    ]
    trust_model = models.ForeignKey(
        TrustModel, on_delete=models.CASCADE, related_name="environments"
    )
    environment = models.CharField(max_length=50, choices=ENV_CHOICES)
    timestamp_server = models.CharField(max_length=255)
    keyshare_server = models.CharField(max_length=255, null=True)
    keyshare_website = models.CharField(max_length=255, null=True)
    keyshare_attribute = models.CharField(max_length=255, null=True)
    contact_website = models.CharField(max_length=255)
    minimum_android_version = models.CharField(max_length=20, null=True)
    minimum_ios_version = models.CharField(max_length=20, null=True)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    description_en = models.TextField()
    description_nl = models.TextField()
    url = models.URLField(validators=[URLValidator()])
    scheme_id = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return f"{self.trust_model.name} - {self.environment}"

    @property
    def scheme_manager(self):
        env_mapping = {
            "production": "pbdf",
            "demo": "irma-demo",
            "development": "pbdf-staging",
            "staging": "pbdf-staging",  # Optional: support alias
        }
        return env_mapping.get(self.environment, "unknown")


class AttestationProvider(models.Model):
    yivi_tme = models.ForeignKey(
        YiviTrustModelEnv,
        on_delete=models.CASCADE,
        related_name="attestation_providers",
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="attestation_providers"
    )
    ap_slug = models.SlugField(null=True, blank=True)
    version = models.CharField(max_length=50)
    shortname_en = models.CharField(max_length=100, null=True, blank=True)
    shortname_nl = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(max_length=255, null=True, blank=True)
    contact_address = models.URLField(null=True, blank=True)
    deprecated_since = models.DateField(null=True, blank=True)
    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(null=True, default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["yivi_tme", "ap_slug"], name="unique_ap_slug_per_yivi_tme"
            )
        ]

    def __str__(self):
        return self.organization.name_en

    @property
    def ap_details(self):
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
    def full_path(self):
        scheme = self.yivi_tme.scheme_manager
        return f"{scheme}.{self.ap_slug}"

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
            self.reviewed_at = timezone.now()
        elif not previous and self.reviewed_accepted:
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
    reviewed_accepted = models.BooleanField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name_en}"

    @property
    def has_invalidated_hostname(self):
        return RelyingPartyHostname.objects.filter(
            relying_party=self,
            dns_challenge_verified=False,
            dns_challenge_invalidated_at__isnull=False,
        ).exists()

    @property
    def status(self) -> str:
        if self.published and self.has_invalidated_hostname:
            return StatusChoices.INVALIDATED
        if self.reviewed_accepted and self.has_invalidated_hostname:
            return StatusChoices.INVALIDATED
        if self.reviewed_accepted is True and self.published:
            return StatusChoices.PUBLISHED
        if self.reviewed_accepted is True and not self.published:
            return StatusChoices.ACCEPTED
        if self.reviewed_accepted is False and not self.published:
            return StatusChoices.REJECTED
        if self.ready:
            return StatusChoices.PENDING_FOR_REVIEW
        return StatusChoices.DRAFT

    def save(self, *args, skip_import_approve=False, **kwargs):

        if self.pk:  # If this record already exists
            if self.ready and not self.ready_at:
                self.ready_at = timezone.now()

            elif not self.ready:  # When it is not ready anymore
                self.ready_at = None
                self.rejection_remarks = None
                self.reviewed_accepted = None
                self.reviewed_at = None

            self.last_updated_at = timezone.now()

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
    deprecated_since = models.DateField(null=True, blank=True)
    name_en = models.CharField(max_length=255, null=True, blank=True)
    name_nl = models.CharField(max_length=255, null=True, blank=True)
    shortname_en = models.CharField(max_length=100, null=True, blank=True)
    shortname_nl = models.CharField(max_length=100, null=True, blank=True)
    credential_id = models.CharField(max_length=100, null=True, blank=True)
    should_be_singleton = models.BooleanField(default=None, null=True, blank=True)
    issue_url = models.URLField(null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)
    description_nl = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name_en

    @property
    def full_path(self):
        scheme = self.attestation_provider.yivi_tme.scheme_manager
        issuer = self.attestation_provider.organization.slug
        return f"{scheme}.{issuer}.{self.credential_id}"


class CredentialAttribute(models.Model):
    credential = models.ForeignKey(
        Credential, on_delete=models.CASCADE, related_name="attributes"
    )
    credential_attribute_tag = models.CharField(max_length=100)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    description_en = models.TextField()
    description_nl = models.TextField()

    class Meta:
        unique_together = ("credential", "name_en")

    def __str__(self):
        return self.name_en

    @property
    def full_path(self):
        return f"{self.credential.full_path}.{self.credential_attribute_tag}"


class RelyingPartyHostname(models.Model):
    DOMAIN_REGEX = (
        r"^(?=^.{1,253}$)(([a-z\d]([a-z\d-]{0,62}[a-z\d])*[\.]){1,3}[a-z]{1,61})$"
    )
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

    def __str__(self):
        return self.hostname


class Condiscon(models.Model):
    condiscon = models.JSONField()
    context_description_en = models.CharField(max_length=255, blank=True, null=True)
    context_description_nl = models.CharField(max_length=255, blank=True, null=True)
    relying_party = models.ForeignKey(
        RelyingParty, on_delete=models.CASCADE, related_name="condiscons"
    )

    def __str__(self):
        return str(self.context_description_en)


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
    email = models.EmailField(max_length=255, null=False, unique=True)
    organizations = models.ManyToManyField(Organization, related_name="users")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email} - {self.role}"
