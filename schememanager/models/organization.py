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

    legal_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    legal_registration_number = models.CharField(
        max_length=100, null=True, blank=True, unique=True
    )
    legal_email = models.EmailField(null=True, blank=True)
    legal_address = models.TextField(null=True, blank=True)
    legal_trade_names = models.JSONField(null=True, blank=True)
    legal_reference_moment = models.DateField(null=True, blank=True)

    billing_email = models.EmailField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    billing_postal_code = models.CharField(max_length=100, null=True, blank=True)
    billing_city = models.CharField(max_length=100, null=True, blank=True)
    billing_country = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.legal_name

    @property
    def name(self):
        return self.legal_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.legal_name)
        return super().save(*args, **kwargs)

    @classmethod
    def create_from_kvk_entry(cls, entry: KvkEntry):
        """Create a new organization based on a KVK entry"""
        # TODO add a lot of logic in here
        organization = cls(
            legal_name=entry.name,
            slug=slugify(entry.name),
            legal_registration_number=entry.kvk_number,
            legal_email=entry.email,
            legal_address=entry.address,
            legal_trade_names=entry.trade_names,
            legal_reference_moment=timezone.datetime.fromisoformat(
                entry.reference_moment
            ),
        )
        organization.full_clean()
        organization.save()
        return organization

    def update_from_kvk_entry(self, entry: KvkEntry):
        """Update an organization based on a KVK entry"""
        # TODO add a lot of logic in here
        self.legal_name = entry.name
        self.slug = slugify(entry.name)
        self.legal_registration_number = entry.kvk_number
        self.legal_email = entry.email
        self.legal_address = entry.address
        self.legal_trade_names = entry.trade_names.split(", ")
        self.legal_reference_moment = timezone.datetime.fromisoformat(
            entry.reference_moment
        )
        self.full_clean()
        self.save()


class OrganizationAdmin(models.Model):
    """A person that is allowed to manage an organization in the system"""

    class Meta:
        unique_together = (("organization", "email"),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="admins"
    )
    email = models.EmailField()

    def __str__(self):
        return f"{self.email} ({self.organization.name})"
