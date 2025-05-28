import datetime
import logging
import json
import os
from io import BytesIO
import zipfile
from django.core.files.images import ImageFile
from urllib.request import urlopen
from portal_backend.models.models import Organization, YiviTrustModelEnv, TrustModel

logger = logging.getLogger(__name__)


def load_config(config_file="/app/config.json") -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_file}: {e}")
        raise


def load_logo_if_exists(logo_path: str) -> ImageFile | None:
    try:
        if not os.path.exists(logo_path):
            logger.error(f"Logo path does not exist: {logo_path}")
            return None

        with open(logo_path, "rb") as logo_file:
            logo_content = logo_file.read()

            if not logo_content:
                logger.error(f"Logo content is empty for path: {logo_path}")
                return None

            filename = os.path.basename(logo_path)
            logo_image_file = ImageFile(BytesIO(logo_content), name=filename)

    except Exception as e:
        logger.error(f"Exception while loading logo from {logo_path}: {e}")
        return None

    return logo_image_file


def create_org(slug: str, name_en: str, name_nl: str, logo_path: str) -> Organization:

    try:
        trust_model = TrustModel.objects.get(name__iexact="yivi")
        logo_image_file = load_logo_if_exists(logo_path)
        org, org_created = Organization.objects.update_or_create(
            slug=slug,
            defaults={
                "is_verified": True,
                "logo": logo_image_file,
                "name_en": name_en,
                "name_nl": name_nl,
                "registration_number": None,
                "city": None,
                "street": None,
                "postal_code": None,
                "house_number": None,
            },
        )

        org.trust_models.add(trust_model)

        logger.info(f"{'Created' if org_created else 'Updated'} Organization: {slug}")
    except Exception as org_error:
        logger.error(f"Failed to create/update Organization {slug}: {org_error}")
        raise

    return org


def normalize_deprecated_since(value: str | None) -> str | None:
    if value is None:
        return None

    try:
        ts = int(value)
        return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid UNIX timestamp for DeprecatedSince: {e}")


def get_trust_model_env(environment: str) -> YiviTrustModelEnv:
    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
    except YiviTrustModelEnv.DoesNotExist:
        raise Exception(
            f"YiviTrustModelEnv for environment '{environment}' does not exist"
        )
    return yivi_tme


def download_extract_repo(repo_url: str, repo_name: str, repo_path: str) -> None:
    os.makedirs("downloads", exist_ok=True)
    logger.info(f"Downloading scheme from {repo_url}")

    try:
        response = urlopen(repo_url)
        repo_zip = zipfile.ZipFile(BytesIO(response.read()))
        repo_zip.extractall(repo_path)
        logger.info(
            f"Successfully extracted zip file to {repo_path}/{repo_name}-master"
        )
    except Exception as e:
        raise Exception(f"Error extracting the zip file: {e}")


def load_json_to_dict(json_path: str) -> dict:
    """Load JSON file to dictionary"""

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            dict = json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load JSON file: {e}")

    logger.info(f"Loaded {len(dict)} items from {json_path}")
    return dict
