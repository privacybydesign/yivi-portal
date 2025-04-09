from django.core.management.base import BaseCommand
from django.utils import timezone
import uuid
from portal_backend.models.models import (
    User,
    Organization,
    TrustModel,
    YiviTrustModelEnv,
    AttestationProvider,
    Credential,
    CredentialAttribute,
)


class Command(BaseCommand):
    help = "Creates test data for development and testing"

    def handle(self, *args, **options):
        # Create test trust model
        trust_model, _ = TrustModel.objects.get_or_create(
            name="Yivi",
            defaults={
                "description": "Test trust model for development",
                "eudi_compliant": False,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created trust model: {trust_model.name}")
        )

        # Create trust model environments
        yivi_tme, _ = YiviTrustModelEnv.objects.get_or_create(
            trust_model=trust_model,
            environment="production",
            defaults={
                "timestamp_server": "https://timestamp.example.com",
                "keyshare_server": "https://keyshare.example.com",
                "keyshare_website": "https://keyshare-web.example.com",
                "keyshare_attribute": "test.keyshare",
                "contact": "contact@example.com",
                "minimum_android_version": "1.0",
                "minimum_ios_version": "1.0",
                "description_en": "Test environment",
                "description_nl": "Testomgeving",
                "url": "https://trust.example.com",
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created trust model environment: {yivi_tme.environment}"
            )
        )

        # Create test organization
        org_id = uuid.uuid4()
        org, _ = Organization.objects.get_or_create(
            id=org_id,
            defaults={
                "name_en": "Test Organization",
                "name_nl": "Testorganisatie",
                "slug": "test-organization",
                "registration_number": "12345678",
                "contact_address": "123 Test Street\nTest City\nTest Country",
                "is_verified": True,
                "verified_at": timezone.now(),
                "trade_names": ["Test Inc.", "Test LLC"],
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created organization: {org.name_en}"))

        # Create test user
        user_email = "test@example.com"
        user, _ = User.objects.get_or_create(
            email=user_email, defaults={"organization": org, "role": "admin"}
        )
        self.stdout.write(self.style.SUCCESS(f"Created user: {user.email}"))

        # Create test attestation provider
        provider, _ = AttestationProvider.objects.get_or_create(
            organization=org,
            yivi_tme=yivi_tme,
            defaults={
                "version": "1.0",
                "shortname_en": "Test Provider",
                "shortname_nl": "Test Provider NL",
                "contact_email": f"contact-{org.id}@example.com",
                "base_url": "https://test.example.com",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(f"Created attestation provider: {provider}")
        )

        # Create test credentials
        email_credential, _ = Credential.objects.get_or_create(
            attestation_provider=provider,
            credential_tag="email",
            defaults={
                "name_en": "Email",
                "name_nl": "E-mail",
                "description_en": "Email credential",
                "description_nl": "E-mail credential",
            },
        )

        mobile_credential, _ = Credential.objects.get_or_create(
            attestation_provider=provider,
            credential_tag="mobile",
            defaults={
                "name_en": "Mobile Phone",
                "name_nl": "Mobiele Telefoon",
                "description_en": "Mobile phone credential",
                "description_nl": "Mobiele telefoon credential",
            },
        )

        # Create test credential attributes
        email_attr, _ = CredentialAttribute.objects.get_or_create(
            credential=email_credential, name="pbdf.pbdf.email.email"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created credential attribute: {email_attr.name} with ID: {email_attr.id}"
            )
        )

        domain_attr, _ = CredentialAttribute.objects.get_or_create(
            credential=email_credential, name="pbdf.pbdf.email.domain"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created credential attribute: {domain_attr.name} with ID: {domain_attr.id}"
            )
        )

        mobile_attr, _ = CredentialAttribute.objects.get_or_create(
            credential=mobile_credential, name="pbdf.pbdf.mobilenumber.mobilenumber"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created credential attribute: {mobile_attr.name} with ID: {mobile_attr.id}"
            )
        )

        # Print test details
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("TEST DATA CREATED SUCCESSFULLY"))
        self.stdout.write(self.style.SUCCESS(f"Organization ID: {org.id}"))
        self.stdout.write(self.style.SUCCESS(f"Test user email: {user.email}"))
        self.stdout.write(self.style.SUCCESS("Credential Attribute IDs for testing:"))
        self.stdout.write(self.style.SUCCESS(f" - Email: {email_attr.id}"))
        self.stdout.write(self.style.SUCCESS(f" - Email Domain: {domain_attr.id}"))
        self.stdout.write(self.style.SUCCESS(f" - Mobile: {mobile_attr.id}"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
