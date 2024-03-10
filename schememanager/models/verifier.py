import hashlib
import json
import os
import secrets
import shutil
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from schememanager.models.organization import Organization
from schememanager.models.scheme import Scheme


class LogoStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            # If the file already exists, delete it, because we want to overwrite it
            # (we base names on the hash of the file)
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


class VerifierRegistrationStatusChoices(models.TextChoices):
    """The possible registration statuses for a verifier"""

    DRAFT = "draft", "Draft"
    REVIEW = "review", "Review"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"  # Rejected after review
    PUBLISHED = "published", "Published"
    INVALIDATED = (
        "invalidated",
        "Invalidated",
    )  # Accepted or published, but became invalid afterward


class Verifier(models.Model):
    """A verifier party that is registered in the system"""

    class Meta:
        unique_together = ("scheme", "slug")

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="verifier_registrations",
        null=True,  # This should be temporary for the migration, TODO remove
        blank=False,
    )
    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.CASCADE,
        limit_choices_to={"scheme_type": Scheme.REQUESTOR},
        null=True,
        blank=False,
    )
    slug = models.SlugField(max_length=100, validators=[MinLengthValidator(5)])

    name_nl = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)

    logo = ProcessedImageField(
        storage=LogoStorage(),
        upload_to=LogoStorage.get_logo_path,
        null=True,
        blank=True,
        processors=[ResizeToFill(300, 300)],
        format="PNG",
        options={"quality": 100},
    )
    approved_logo = models.ImageField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(default=None, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_scheme_data = models.JSONField(null=True, blank=True)
    rejection_remarks = models.TextField(null=True, blank=True)

    published_scheme_data = models.JSONField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reviewed_accepted = self.reviewed_accepted
        self._logo = self.logo
        self._scheme = self.scheme

    def __str__(self):
        return (
            f"{self.name_en} ({self.full_id})"
            if self.name_en
            else f"{self.organization.name} ({self.full_id})"
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)

        if self._logo != self.logo and self._logo:
            # If the logo has changed, delete the old one
            # But only if no other verifier is using it, and it's not in the approved scheme data
            # So effectively, we keep a copy of all logos that have ever been approved

            if (
                not Verifier.objects.filter(
                    Q(logo=self._logo) | Q(approved_logo=self._logo)
                )
                .exclude(id=self.id)
                .exists()
            ) and not self.approved_logo == self._logo:
                self.logo.storage.delete(self._logo.path)

        if self._reviewed_accepted != self.reviewed_accepted:
            if self.reviewed_accepted:
                self._make_accepted()
            elif self.reviewed_accepted is not None:
                self._make_rejected()

        if self.status == VerifierRegistrationStatusChoices.REVIEW:
            self.reviewed_accepted = None

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.logo:
            if (
                not Verifier.objects.filter(
                    Q(logo=self.logo) | Q(approved_logo=self.logo)
                )
                .exclude(id=self.id)
                .exists()
            ):
                storage, path = self.logo.storage, self.logo.path
                storage.delete(path)

        if self.approved_logo:
            if (
                not Verifier.objects.filter(
                    Q(logo=self.approved_logo) | Q(approved_logo=self.approved_logo)
                )
                .exclude(id=self.id)
                .exists()
            ):
                storage, path = self.approved_logo.storage, self.approved_logo.path
                storage.delete(path)

        super().delete(*args, **kwargs)

    def _make_accepted(self):
        self.reviewed_accepted = True
        self.reviewed_at = timezone.now()
        self.rejection_remarks = None
        self.approved_scheme_data = self.new_scheme_data
        self.approved_logo = self.logo

    def _make_rejected(self):
        self.reviewed_accepted = False
        self.reviewed_at = timezone.now()
        self.approved_scheme_data = self.published_scheme_data

    def accept(self):
        self._make_accepted()
        self.save()

    def reject(self, remarks: str):
        self._make_rejected()
        self.rejection_remarks = remarks
        self.save()

    @property
    def status(self):
        if self.invalidated:
            return VerifierRegistrationStatusChoices.INVALIDATED
        elif self.ready and self.published:
            return VerifierRegistrationStatusChoices.PUBLISHED
        elif self.rejected:
            return VerifierRegistrationStatusChoices.REJECTED
        elif self.accepted or (
            self.ready and self.valid and not self.scheme.production
        ):
            return VerifierRegistrationStatusChoices.ACCEPTED
        elif self.ready and self.valid:
            return VerifierRegistrationStatusChoices.REVIEW
        return VerifierRegistrationStatusChoices.DRAFT

    @property
    def invalidated(self):
        return (
            (
                self.approved_scheme_data == self.published_scheme_data
                or self.reviewed_accepted
            )
            and self.unverified_hostnames.exclude(
                dns_challenge_verified_at__isnull=True
            ).exists()
            and self.ready
        )

    @property
    def published(self):
        if self.published_scheme_data and (
            self.approved_scheme_data == self.published_scheme_data
            and self.new_scheme_data == self.published_scheme_data
            or not self.approved_scheme_data
            and self.new_scheme_data == self.published_scheme_data
        ):
            return True
        return False

    @property
    def rejected(self):
        return not self.reviewed_accepted and self.reviewed_accepted is not None

    @property
    def accepted(self):
        return (
            self.reviewed_accepted and self.new_scheme_data == self.approved_scheme_data
        )

    def validate_for_publication(self):
        """Validate if the verifier is ready to be published."""
        errors = {}
        if not self.name_nl:
            errors["name_nl"] = "No Dutch name has been provided"
        if not self.name_en:
            errors["name_en"] = "No English name has been provided"
        if not self.logo:
            errors["logo"] = "No logo has been uploaded"

        if (
            not self.pk
        ):  # If the verifier is not saved yet, we can't validate it further
            return

        if not self.hostnames.exists():
            errors["hostnames"] = "No hostnames have been provided"
        if self.unverified_hostnames.exists():
            errors["hostnames"] = "Not all hostnames have been verified"

        sessions_no_context = self.session_requests.filter(
            Q(context_description_en="")
            | Q(context_description_nl="")
            | Q(context_description_nl__isnull=True)
            | Q(context_description_en__isnull=True)
        )
        if sessions_no_context.exists():
            errors[
                "session_requests"
            ] = "Not all session requests have a context description provided"

        if settings.USE_SESSION_REQUEST_REGISTRATION:
            unspecified_attributes = self.session_requests.filter(
                Q(attributes__reason_en="") | Q(attributes__reason_nl="")
            )
            if unspecified_attributes.exists():
                errors[
                    "session_requests_attrs"
                ] = "Not all attributes have a reason for requesting provided"

        return errors

    @property
    def valid(self):
        return not self.validate_for_publication()

    @property
    def unverified_hostnames(self):
        if not self.id:
            return VerifierHostname.objects.none()
        return self.hostnames.filter(
            dns_challenge_verified=False, manually_verified=False
        )

    @property
    def logo_name(self):
        name = os.path.basename(self.logo.name)
        return os.path.splitext(name)[0]

    @property
    def new_scheme_data(self):
        scheme = {
            "id": self.full_id,
            "name": {
                "en": self.name_en,
                "nl": self.name_nl,
            },
            "logo": self.logo_name if self.logo else None,
            "hostnames": [hostname.hostname for hostname in self.hostnames.all()]
            if self.pk
            else [],
            "scheme": self.scheme.id,
        }
        if settings.USE_SESSION_REQUEST_REGISTRATION:
            scheme["requests"] = [
                {
                    "condiscon": session.condiscon,
                    "context": {
                        "en": session.context_description_en,
                        "nl": session.context_description_nl,
                    },
                    "reason": {
                        str(session.condiscon_attributes.index(attr.attribute_id)): {
                            "en": attr.reason_en,
                            "nl": attr.reason_nl,
                        }
                        for attr in session.attributes.all()
                    },
                }
                for session in self.session_requests.all()
            ]
        return scheme

    @property
    def new_scheme_data_json(self):
        return (
            json.dumps(self.new_scheme_data, indent=4) if self.new_scheme_data else None
        )

    @property
    def published_scheme_data_json(self):
        return (
            json.dumps(self.published_scheme_data, indent=4)
            if self.published_scheme_data
            else None
        )

    @property
    def approved_scheme_data_json(self):
        return (
            json.dumps(self.approved_scheme_data, indent=4)
            if self.approved_scheme_data
            else None
        )

    @property
    def display_name(self):
        if self.name_en:
            return self.name_nl
        return self.organization.name

    @property
    def full_id(self):
        return f"{self.scheme}.{self.slug}"

    @property
    def can_be_edited(self):
        return self.status in [
            VerifierRegistrationStatusChoices.DRAFT,
            VerifierRegistrationStatusChoices.REVIEW,
            VerifierRegistrationStatusChoices.REJECTED,
            VerifierRegistrationStatusChoices.INVALIDATED,
        ]

    def get_absolute_url(self):
        return reverse(
            "schememanager:verifier-portal",
            args=[self.scheme.id, self.slug],
        )


class VerifierHostname(models.Model):
    """A hostname that is registered for a verifier"""

    class Meta:
        unique_together = (("hostname", "verifier"),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=100)
    verifier = models.ForeignKey(
        Verifier, on_delete=models.CASCADE, related_name="hostnames"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    dns_challenge = models.CharField(max_length=100, null=True, blank=True)
    dns_challenge_created_at = models.DateTimeField(null=True, blank=True)
    dns_challenge_verified = models.BooleanField(default=False)
    dns_challenge_verified_at = models.DateTimeField(null=True, blank=True)
    dns_challenge_invalidated_at = models.DateTimeField(null=True, blank=True)

    manually_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if (
            existing := VerifierHostname.objects.filter(hostname=self.hostname)
            .exclude(id=self.id)
            .first()
        ):
            # If the hostname already exists for a different scheme, copy the DNS challenge data
            if self.dns_challenge != existing.dns_challenge:
                self.dns_challenge = existing.dns_challenge
                self.dns_challenge_created_at = existing.dns_challenge_created_at
                self.dns_challenge_verified = existing.dns_challenge_verified
                self.dns_challenge_verified_at = existing.dns_challenge_verified_at

        if self.dns_challenge is None:
            self.refresh_dns_challenge()

        return super().save(*args, **kwargs)

    def refresh_dns_challenge(self):
        random = secrets.token_hex(16)
        self.dns_challenge = f'"yivi_verifier_challenge={random}"'
        self.dns_challenge_created_at = timezone.now()
        self.dns_challenge_verified = False
        self.dns_challenge_verified_at = None
        self.dns_challenge_invalidated_at = None

    def __str__(self):
        return f"{self.hostname} ({self.verifier.name_en})"


class VerifierSessionRequest(models.Model):
    """A Yivi session request that a verifier registers in the system"""

    verifier = models.ForeignKey(
        Verifier, on_delete=models.CASCADE, related_name="session_requests"
    )
    condiscon = models.JSONField()

    context_description_en = models.CharField(max_length=255, null=True, blank=True)
    context_description_nl = models.CharField(max_length=255, null=True, blank=True)

    @property
    def condiscon_json(self):
        return json.dumps(self.condiscon)

    @property
    def condiscon_attributes(self):
        """Return all attributes that are requested in the condiscon"""
        if not self.condiscon or "disclose" not in self.condiscon:
            raise ValidationError("Invalid condiscon")
        return list(
            attribute
            for discon in self.condiscon["disclose"]
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

    def __str__(self):
        if self.context_description_en:
            return f"{self.verifier.name_en} - {self.condiscon_json} - {self.context_description_en}"
        return f"{self.verifier.name_en} - {self.condiscon_json}"


class VerifierAttributeRequest(models.Model):
    """An attribute that a verifier requests in a session"""

    session = models.ForeignKey(
        VerifierSessionRequest, on_delete=models.CASCADE, related_name="attributes"
    )
    attribute_id = models.CharField(max_length=100)
    reason_en = models.TextField()
    reason_nl = models.TextField()

    def __str__(self):
        return f"{self.attribute_id} ({self.session})"
