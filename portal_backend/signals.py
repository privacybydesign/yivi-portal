from typing import Type, Any

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models.models import RelyingParty, Status, Organization


# --------- RELYING PARTY SIGNALS ----------
@receiver(post_save, sender=RelyingParty)
def create_status_for_relying_party(
    sender: Type[RelyingParty], instance: RelyingParty, created: bool, **kwargs: Any
) -> None:
    if created:
        Status.objects.create(relying_party=instance)
        print(f"Status created for RelyingParty {instance}")


@receiver(post_delete, sender=RelyingParty)
def delete_status_for_relying_party(
    sender: Type[RelyingParty], instance: RelyingParty, **kwargs: Any
) -> None:
    try:
        if hasattr(instance, "status"):
            instance.status.delete()
            print(f"Status deleted for RelyingParty {instance}")
    except Status.DoesNotExist:
        pass


# --------- ORGANIZATION SIGNALS ----------
@receiver(pre_save, sender=Organization)
def save_logo_as_approved_logo(
    sender: Type[Organization], instance: Organization, **kwargs: Any
) -> None:
    if instance.is_verified:
        instance.approved_logo = instance.logo
        print(f"Approved logo set for Organization {instance}")
