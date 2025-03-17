from django.core.files.images import ImageFile
import json
import os
from dotenv import load_dotenv
import zipfile
from django.db import transaction
from urllib.request import urlopen
from io import BytesIO
from portal_backend.models.models import (
    RelyingParty,
    Organization,
    RelyingPartyHostname,
    YiviTrustModelEnv,
)
import logging


logger = logging.getLogger(__name__)
load_dotenv()


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


def download_extract_scheme(url, repo_name):
    os.makedirs("downloads", exist_ok=True)
    logger.info(f"Downloading schema from {url}")
    response = urlopen(url)
    repo_zip = zipfile.ZipFile(BytesIO(response.read()))
    try:
        repo_zip.extractall("downloads/relying-party-repo")
        logger.info(
            f"Successfully extracted zip file to downloads/relying-party-repo/{repo_name}-master"
        )
    except Exception as e:
        logger.error(f"Error extracting the zip file: {e}")


@transaction.atomic
def create_update_RPs(repo_folder, environment):
    """
    Create relying parties and the corresponding organization and hostnames
    for a specific YiviTrustModelEnv (environment)
    """
    requestors_json_path = os.path.join(repo_folder, "requestors.json")
    if not os.path.exists(requestors_json_path):
        logger.error(f"requestors.json not found in {repo_folder}")
        return False

    try:
        with open(requestors_json_path, "r", encoding="utf-8") as f:
            rp_list = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load requestors.json: {e}")
        return False

    logger.info(f"Found {len(rp_list)} verifiers in the JSON.")

    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
    except YiviTrustModelEnv.DoesNotExist:
        logger.error(
            f"YiviTrustModelEnv for environment '{environment}' does not exist!"
        )
        return False

    for rp_data in rp_list:
        try:
            try:
                slug = rp_data["id"].split(".")[1]
            except (KeyError, IndexError):
                logger.error(
                    f"Invalid ID format in relying party data: {rp_data.get('id', 'unknown')}"
                )
                continue

            hostnames = rp_data.get("hostnames", [])
            if not hostnames:
                logger.warning(f"No hostnames found for {slug}")
                return

            name_en = rp_data.get("name", {}).get("en", slug)
            name_nl = rp_data.get("name", {}).get("nl", slug)
            logo_hash = rp_data.get("logo")

            if not logo_hash:
                logger.warning(f"No logo found for {rp_data['id']}")
                continue

            logo_path = os.path.join(repo_folder, "assets", f"{logo_hash}.png")
            if not os.path.exists(logo_path):
                logger.warning(f"Logo file not found: {logo_path}")
                continue

            with open(logo_path, "rb") as logo_file:
                logo_image_file = ImageFile(logo_file, name=f"{logo_hash}.png")

                try:
                    org, org_created = Organization.objects.update_or_create(
                        slug=slug,
                        defaults={
                            "is_verified": True,
                            "logo": logo_image_file,
                            "name_en": name_en,
                            "name_nl": name_nl,
                            "registration_number": "AUTO-GENERATED",
                            "contact_address": "AUTO-GENERATED",
                        },
                    )
                    logger.info(
                        f"{'Created' if org_created else 'Updated'} Organization: {slug}"
                    )
                except Exception as org_error:
                    logger.error(
                        f"Failed to create/update Organization {slug}: {org_error}"
                    )
                    continue

            try:
                rp_obj, rp_created = RelyingParty.objects.update_or_create(
                    organization=org,
                    yivi_tme=yivi_tme,
                    defaults={
                        "approved_rp_details": rp_data,
                        "published_rp_details": rp_data,
                    },
                )

                if rp_created:
                    logger.info(
                        f"Created new RelyingParty for {slug} in environment '{environment}'"
                    )  # if RP with same env existed it will update otherwise it will be created
                else:
                    logger.info(
                        f"Updated existing RelyingParty for {slug} in environment '{environment}'"
                    )

            except Exception as rp_error:
                logger.error(
                    f"Failed to create/update RelyingParty for {slug}: {rp_error}"
                )
                continue

            for hostname in hostnames:
                try:
                    rp_hostname, hostname_created = (
                        RelyingPartyHostname.objects.update_or_create(
                            relying_party=rp_obj,
                            hostname=hostname,
                            defaults={
                                "manually_verified": True,
                                "dns_challenge": None,
                                "dns_challenge_created_at": None,
                            },
                        )
                    )
                    logger.info(
                        f"{'Created' if hostname_created else 'Updated'} Hostname: {hostname} for RP {slug} in environment '{environment}'"
                    )
                except Exception as hostname_error:
                    logger.error(
                        f"Failed to create/update Hostname {hostname} for RP {slug}: {hostname_error}"
                    )

        except Exception as e:
            logger.error(
                f"Failed to process RP {rp_data.get('id', 'unknown')} in environment '{environment}': {e}"
            )

    logger.info(f"Import summary for environment '{environment}'")
    return True


# download requestors repo
def import_rps():
    config = load_config()
    env_value = os.environ.get("RP_ENV")
    logger.info(f"Current RP_ENV value: {env_value}")

    if env_value == "production":
        repo_url = config["RP"]["environment"]["production"]["repo-url"]
        repo_name = config["RP"]["environment"]["production"]["name"]
        environment = "production"
    elif env_value == "demo":
        logger.error("Demo environment is not in supported structure yet.")
    else:
        logger.error(f"No specific environment specified. Got: '{env_value}'")
        return False

    try:
        download_extract_scheme(repo_url, repo_name)
        logger.info(f"Downloaded requestors scheme from {repo_url}")
    except Exception as e:
        logger.error(f"Failed to download and extract schema: {e}")
        return False

    repo_folder = f"downloads/relying-party-repo/{repo_name}-master"
    if not os.path.exists(repo_folder):
        logger.error(f"Repository folder not found: {repo_folder}")
        return False

    success = create_update_RPs(repo_folder, environment)

    if success:
        logger.info(f"Import completed successfully for environment '{environment}'")
        return True
    else:
        logger.error(f"Import failed for environment '{environment}'")
        return False
