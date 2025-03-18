import logging
import json
import os
from io import BytesIO
from django.core.files.images import ImageFile
from portal_backend.models.models import Organization, YiviTrustModelEnv

logger = logging.getLogger(__name__)


def load_config(config_file="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_file}: {e}")
        raise


def load_logo_if_exists(logo_path: str):
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as logo_file:
            logo_content = logo_file.read()
            logo_image_file = ImageFile(BytesIO(logo_content))
            return logo_image_file
    else:
        logger.error(f"Logo file not found at {logo_path}")
        return None


def create_org(slug, name_en, name_nl, logo_path):

    try:
        logo_image_file = load_logo_if_exists(logo_path)
        org, org_created = Organization.objects.update_or_create(
            slug=slug,
            defaults={
                "is_verified": True,
                "logo": logo_image_file,
                "name_en": name_en,
                "name_nl": name_nl,
                "registration_number": None,
                "contact_address": None,
            },
        )
        logger.info(f"{'Created' if org_created else 'Updated'} Organization: {slug}")
        return org
    except Exception as org_error:
        logger.error(f"Failed to create/update Organization {slug}: {org_error}")
        raise


def get_trust_model_env(environment: str):
    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
        return yivi_tme
    except YiviTrustModelEnv.DoesNotExist:
        raise Exception(
            f"YiviTrustModelEnv for environment '{environment}' does not exist"
        )
