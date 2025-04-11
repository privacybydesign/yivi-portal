from typing import Type, Any

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models.models import Organization


# --------- ORGANIZATION SIGNALS ----------
@receiver(pre_save, sender=Organization)
def save_logo_as_approved_logo(
    sender: Type[Organization], instance: Organization, **kwargs: Any
) -> None:
    if instance.is_verified:
        instance.approved_logo = instance.logo
        print(f"Approved logo set for Organization {instance}")
