import json
import secrets
import uuid
from dataclasses import dataclass

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


@dataclass
class KvkEntry:
    kvk_number: str
    name: str
    trade_names: str
    type_owner: str
    legal_entity: str
    address: str
    email: str
    phone: str
    registration_start: str
    date_deregistration: str
    registration_end: str
    special_legal_situation: str
    restriction_in_legal_action: str
    foreign_legal_status: str
    has_restriction: str
    is_authorized: str
    reason: str
    reference_moment: str


class Organization(models.Model):
    """A registered organization in the system (can be both an issuer and a verifier)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    kvk_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    kvk_registration_start = models.DateField(null=True, blank=True)
    kvk_registration_end = models.DateField(null=True, blank=True)
    kvk_email = models.EmailField(null=True, blank=True)

    billing_email = models.EmailField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    billing_postal_code = models.CharField(max_length=100, null=True, blank=True)
    billing_city = models.CharField(max_length=100, null=True, blank=True)
    billing_country = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @classmethod
    def create_from_kvk_entry(cls, entry: KvkEntry):
        """Create a new organization based on a KVK entry"""
        # TODO add a lot of logic in here
        organization = cls(
            name=entry.name,
            slug=slugify(entry.name),
            kvk_number=entry.kvk_number,
        )
        organization.save()
        return organization


class OrganizationAdmin(models.Model):
    """A person that is allowed to manage an organization in the system"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="admins"
    )
    email = models.EmailField()

    def __str__(self):
        return f"{self.email} ({self.organization.name})"

    class Meta:
        unique_together = (("organization", "email"),)


class Scheme(models.Model):
    """A scheme that is registered in the system"""

    REQUESTOR = "requestor"
    ISSUER = "issuer"

    SCHEME_TYPES = (
        (REQUESTOR, "Requestor"),
        (ISSUER, "Issuer"),
    )

    id = models.SlugField(max_length=100, primary_key=True)
    scheme_type = models.CharField(max_length=10, choices=SCHEME_TYPES)

    def __str__(self):
        return self.id


def get_new_logo_path(instance, filename):
    """Determine the path for a logo image"""
    unique_id = secrets.token_hex(8)
    return f"logos/{instance.scheme.id}/{instance.slug}-{unique_id}.png"


class Verifier(models.Model):
    """A verifier party that is registered in the system"""

    organization = models.OneToOneField(
        Organization,
        on_delete=models.PROTECT,
        related_name="verifier",
    )

    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.CASCADE,
        limit_choices_to={"scheme_type": Scheme.REQUESTOR},
        null=True,
        blank=False,
    )
    slug = models.SlugField(max_length=100)

    name_nl = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_nl = models.TextField(null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)

    logo = models.ImageField(upload_to=get_new_logo_path, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name_en} ({self.scheme}.{self.slug})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = (("scheme", "slug"),)


class VerifierHostname(models.Model):
    """A hostname that is registered for a verifier"""

    hostname = models.CharField(max_length=100, primary_key=True)
    verifier = models.ForeignKey(
        Verifier, on_delete=models.CASCADE, related_name="hostnames"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    dns_challenge = models.CharField(max_length=100, null=True, blank=True)
    dns_challenge_created_at = models.DateTimeField(null=True, blank=True)
    dns_challenge_verified = models.BooleanField(default=False)
    dns_challenge_verified_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.dns_challenge:
            self.refresh_dns_challenge()

        return super().save(*args, **kwargs)

    def refresh_dns_challenge(self):
        random = secrets.token_hex(16)
        self.dns_challenge = f'"yivi_verifier_challenge={random}"'
        self.dns_challenge_created_at = timezone.now()
        self.dns_challenge_verified = False
        self.dns_challenge_verified_at = None

    def __str__(self):
        return f"{self.hostname} ({self.verifier.name_en})"


class VerifierSessionRequest(models.Model):
    """A Yivi session request that a verifier registers in the system"""

    verifier = models.ForeignKey(
        Verifier, on_delete=models.CASCADE, related_name="session_requests"
    )
    condiscon = models.JSONField()

    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True)

    context_description_en = models.TextField(null=True)
    context_description_nl = models.TextField(null=True)

    @property
    def condiscon_attributes(self):
        """Return all attributes that are requested in the condiscon"""
        condiscon = json.loads(self.condiscon)
        return list(
            attribute
            for discon in condiscon["disclose"]
            for con in discon
            for attribute in con
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.refresh_from_db()
        for attribute in self.condiscon_attributes:
            VerifierAttributeRequest.objects.get_or_create(
                session=self,
                attribute_id=attribute,
                defaults={
                    "reason_en": "",
                    "reason_nl": "",
                },
            )
        self.attributes.exclude(attribute_id__in=self.condiscon_attributes).delete()


class VerifierAttributeRequest(models.Model):
    """An attribute that a verifier requests in a session"""

    session = models.ForeignKey(
        VerifierSessionRequest, on_delete=models.CASCADE, related_name="attributes"
    )
    attribute_id = models.CharField(max_length=100)
    reason_en = models.TextField()
    reason_nl = models.TextField()
