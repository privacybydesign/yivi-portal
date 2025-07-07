import os
import requests
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from portal_backend.models.models import Organization, RelyingParty

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
YIVI_PORTAL_URL = os.environ.get("YIVI_PORTAL_URL")
logger = logging.getLogger(__name__)


def notify_slack(text, webhook_url):
    payload = {"text": text}
    requests.post(webhook_url, json=payload)


def slack_notify_handler(input: str) -> None | Exception:
    try:
        notify_slack(input, SLACK_WEBHOOK_URL)
    except Exception as e:
        logger.warning(
            "Couldn't send Slack notification for organization creation due to an error: %s",
            e,
        )


@receiver(post_save, sender=Organization)
def notify_organization_creation(sender, instance, created, **kwargs):
    if created:
        text = f"New organization created: {instance.name_en} on {YIVI_PORTAL_URL} (ID: {instance.id})  "
        slack_notify_handler(text)


@receiver(post_save, sender=RelyingParty)
def notify_relying_party_creation(sender, instance, created, **kwargs):
    if created:
        text = f"New relying party created: {instance.rp_slug} on {YIVI_PORTAL_URL} (ID: {instance.id}) "
        slack_notify_handler(text)
    if instance.tracker.has_changed("ready") and instance.ready:
        text = f"Relying party '{instance.rp_slug}' is now READY FOR REVIEW on {YIVI_PORTAL_URL} (ID: {instance.id})"
        slack_notify_handler(text)
