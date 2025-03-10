from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import URLValidator, RegexValidator
import uuid
from django.utils import timezone

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
    
class AttestationProvider(models.Model):
    yivi_tme = models.ForeignKey(YiviTrustModelEnv, on_delete=models.CASCADE, related_name='attestation_providers')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='attestation_providers')
    version = models.CharField(max_length=50)
    shortname_en = models.CharField(max_length=100)
    shortname_nl = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=255, unique=True)
    base_url = models.URLField()
    approved_ap_details = models.JSONField(null=True) # what will be added to issuers scheme
    published_ap_details = models.JSONField(null=True) # what is actually published 

    def __str__(self):
        return self.organization.name_en    

class RelyingParty(models.Model):
    class Meta:
        verbose_name = 'Relying Party'
        verbose_name_plural = 'Relying Parties'
    yivi_tme = models.ForeignKey(YiviTrustModelEnv, on_delete=models.CASCADE, related_name='relying_parties')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='relying_parties')
    approved_rp_details = models.JSONField(null=True) # what will be added to requestors scheme (formerly called scheme data)
    published_rp_details = models.JSONField(null=True)

    def __str__(self):
        return f"{self.organization.name_en}"
    
    @property
    def new_rp_details(self):
        hostname = RelyingPartyHostname.objects.filter(relying_party=self).first()
        requestor_scheme_entry = {
            "id": self.id,
            "name": {
                "en": self.organization.name_en,
                "nl": self.organization.name_nl
            },
            "logo": self.organization.logo.url, # will need to be the hash of the logo
            "hostnames": [hostname.hostname], # right now the verifier can only have one hostname
            "scheme": self.yivi_tme.environment,
        }
        return requestor_scheme_entry



     # construct new rp details based on RP hostname , condiscon and rest of needed data

    @property
    def approve(self):
        pass # put new_rp_details in approved_rp_details

    @property
    def published_rp_details(self):
        pass # published_check checks if this rp is published and returns the published_rp_details

    
    
class StatusChoices(models.TextChoices):
    """Choices for the status of a Relying Party or Attestation Provider."""

    DRAFT = 'draft', 'Draft'
    PENDING_FOR_REVIEW = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'
    PUBLISHED = 'published', 'Published'
    INVALIDATED = 'invalidated', 'Invalidated' # the ap or rp became invalid after being published, possibly due to a failure in dns_challenge  (for the rp)

class Status(models.Model):
    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
        constraints = [
        CheckConstraint(     check=Q(relying_party__isnull=False, attestation_provider__isnull=True) | 
                                   Q(relying_party__isnull=True, attestation_provider__isnull=False),
                            name='either_rp_or_ap',)
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    ready = models.BooleanField(default=False)
    ready_at = models.DateTimeField(null=True, blank=True)
    reviewed_accepted = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    relying_party = models.OneToOneField(RelyingParty, on_delete=models.CASCADE, related_name='status', null=True, blank=True)
    attestation_provider = models.OneToOneField(AttestationProvider, on_delete=models.CASCADE, related_name='status', null=True, blank=True)
    approved_provider_details = models.JSONField(null=True) # what will be added to requestors scheme (formerly called scheme data)
    published_provider_details = models.JSONField(null=True) # what is actually published (formerly called published scheme data)



    @property
    def published(self):
        return self.approved_provider_details == self.published_provider_details and self.published_at is not None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_ready = self.ready
        self._initial_reviewed_accepted = self.reviewed_accepted
        self._initial_published = self.published
        self._initial_rejection_remarks = None

    def save(self, *args, **kwargs): # state transition logic
        if  self.ready and not self._initial_ready:  # if ready is changed to True from inital False
            if self.ready:
                self.ready_at = timezone.now()
            # status will be PENDING FOR REVIEW
            elif self._initial_ready and not self.ready: # if ready is changed to False
                self.ready_at = None
                self.reviewed_accepted = None
                self.reviewed_at = None
                self.rejection_remarks = None
                self.published_at = None
             # if the user unchecks the ready checkbox, the status will go back DRAFT and all other fields will reset

        if self.reviewed_accepted and not self._initial_reviewed_accepted:  #  if reviewed_accepted is changed to True
            if self.reviewed_accepted:
                self.reviewed_at = timezone.now()
                # status will be ACCEPTED
                self.rejection_remarks = None
            elif self._initial_reviewed_accepted and not self.reviewed_accepted: # if reviewed_accepted is changed to False
                self.reviewed_at = timezone.now()
                self._initial_rejection_remarks = self.rejection_remarks
                # status will be REJECTED

        if self.published and not self._initial_published: # if published is changed to True
            self.published_at = timezone.now()
            # status will be PUBLISHED

        self._initial_ready = self.ready # save initial states for future comparisons
        self._initial_reviewed_accepted = self.reviewed_accepted
        self._initial_published = self.published
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"Status {self.id} - Ready: {self.ready}"

    @property
    def rp_status(self):
        rphostname = RelyingPartyHostname.objects.filter(relying_party=self.relying_party).first()
        if rphostname and self.published and rphostname.invalidated: # if rp is published and then dns_challenge is invalidated
            return StatusChoices.INVALIDATED
        elif self.ready and self.published:
            return StatusChoices.PUBLISHED
        elif self.reviewed_accepted is False:
            return StatusChoices.REJECTED
        elif self.reviewed_accepted is True:
            return StatusChoices.ACCEPTED
        elif self.ready:
            return StatusChoices.PENDING_FOR_REVIEW
        return StatusChoices.DRAFT
    

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
        return self.name
    
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
    relying_party = models.OneToOneField(RelyingParty, on_delete=models.CASCADE, related_name='hostnames')
    

    @property
    def invalidated(self): # TODO if dns_challenge is invalidated or if the published_rp_details is now different than approved_rp_details
        return self.dns_challenge_verified and self.dns_challenge_invalidated_at is not None
    
    
    def __str__(self):
        return self.hostname

class Condiscon(models.Model):
    condiscon = models.JSONField()
    context_description_en = models.CharField(max_length=255)
    context_description_nl = models.CharField(max_length=255)
    relying_party = models.ForeignKey(RelyingParty, on_delete=models.CASCADE, related_name='condiscons')


    def __str__(self):
        return str(self.condiscon)
    
class CondisconAttribute(models.Model):
    credential_attribute = models.ForeignKey(CredentialAttribute, on_delete=models.CASCADE, related_name='condiscon_attributes')
    condiscon = models.ForeignKey(Condiscon, on_delete=models.CASCADE)
    reason_en = models.TextField()
    reason_nl = models.TextField()
    
    def __str__(self):
        return f"{self.credential_attribute.credential.name_en}"
    
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('maintainer', 'Maintainer'),
    ]
    email = models.EmailField(max_length=255, unique=True , null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users', null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.organization.name_en} - {self.role}"
    