from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models.models import RelyingParty, AttestationProvider, Status

# --------- RELYING PARTY SIGNALS ----------

@receiver(post_save, sender=RelyingParty)
def create_status_for_relying_party(sender, instance, created, **kwargs):
    if created:
        Status.objects.create(relying_party=instance)
        print(f"Status created for RelyingParty {instance}")

@receiver(post_delete, sender=RelyingParty)
def delete_status_for_relying_party(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'status'):
            instance.status.delete()
            print(f"Status deleted for RelyingParty {instance}")
    except Status.DoesNotExist:
        pass
