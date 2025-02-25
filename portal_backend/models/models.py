from django.db import models
from django.core.validators import URLValidator, RegexValidator
import uuid

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    registration_number = models.CharField(max_length=100)
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(auto_now_add=True)
    trade_names = models.JSONField(default=list)
    logo = models.ImageField(upload_to='organization/logos/')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name_en

class TrustModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    eudi_compliant = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class YiviTrustModelEnv(models.Model):
    ENV_CHOICES = [
        ('production', 'Production'),
        ('development', 'Development'),
        ('Demo', 'Demo'),
    ]
    trust_model = models.ForeignKey(TrustModel, on_delete=models.CASCADE, related_name='environments')
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

class ApplicationStatus(models.Model):
    class Meta:
        verbose_name = 'Application status'
        verbose_name_plural = 'Application statuses'
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Status {self.id} - Ready: {self.ready}"

class RelyingPartyHostname(models.Model):
    DOMAIN_REGEX = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,6})+$'
    hostname = models.CharField(
        max_length=255,
        unique=True,
        validators=[RegexValidator(
            regex=DOMAIN_REGEX,
            message="Enter a valid domain (e.g., example.com).",
            code="invalid_domain"
        )]
    )
    dns_challenge = models.CharField(max_length=255)
    dns_challenge_created_at = models.DateTimeField()
    dns_challenge_verified = models.BooleanField(default=False)
    dns_challenge_verified_at = models.DateTimeField(null=True, blank=True)
    dns_challenge_invalidated_at = models.DateTimeField(null=True, blank=True)
    manually_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname

class Condiscon(models.Model):
    condiscon = models.JSONField()
    context_description_en = models.CharField(max_length=255)
    context_description_nl = models.CharField(max_length=255)

    def __str__(self):
        return str(self.condiscon)


class AttestationProvider(models.Model):
    yivi_tme = models.ForeignKey(YiviTrustModelEnv, on_delete=models.CASCADE, related_name='attestation_providers')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='attestation_providers')
    status = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    shortname_en = models.CharField(max_length=100)
    shortname_nl = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=255, unique=True)
    base_url = models.URLField()

    def __str__(self):
        return self.organization.name_en

class Credential(models.Model):
    attestation_provider = models.ForeignKey(AttestationProvider, on_delete=models.CASCADE, related_name='credentials')
    credential_tag = models.CharField(max_length=100)
    name_en = models.CharField(max_length=255)
    name_nl = models.CharField(max_length=255)
    description_en = models.TextField()
    description_nl = models.TextField()

    def __str__(self):
        return self.name_en

class CredentialAttribute(models.Model):
    name = models.CharField(max_length=255)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE, related_name='attributes')

    class Meta:
        unique_together = ('credential', 'name')

    def __str__(self):
        return f"{self.credential.name_en} - {self.name}"

class CondisconAttribute(models.Model):
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)
    condiscon = models.ForeignKey(Condiscon, on_delete=models.CASCADE)
    reason_en = models.TextField()
    reason_nl = models.TextField()


    def __str__(self):
        return f"{self.credential.name_en} - {self.reason_en}"

class RelyingParty(models.Model):
    class Meta:
        verbose_name = 'Relying Party'
        verbose_name_plural = 'Relying Parties'
    yivi_tme = models.ForeignKey(YiviTrustModelEnv, on_delete=models.CASCADE, related_name='relying_parties')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='relying_parties')
    status = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)
    hostname = models.ForeignKey(RelyingPartyHostname, on_delete=models.CASCADE)
    condiscon = models.ForeignKey(Condiscon, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.organization.name_en}"

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('maintainer', 'Maintainer'),
    ]
    email = models.EmailField(max_length=255, unique=True , null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.organization.name_en} - {self.role}"