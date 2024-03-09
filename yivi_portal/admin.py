import logging

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver

admin.site.site_header = "Yivi Portal Admin"

logger = logging.getLogger()


@receiver(post_save, sender=LogEntry)
def log_admin_action(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Admin user {instance.user.username} on {instance.object_repr}: {instance.change_message}"
        )
