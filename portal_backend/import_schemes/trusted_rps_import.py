import json
import os
from dotenv import load_dotenv
import zipfile
from django.db import transaction
from urllib.request import urlopen
from io import BytesIO
from portal_backend.models.models import (
    RelyingParty,
    RelyingPartyHostname,
)
import logging
import portal_backend.import_schemes.import_utils as import_utils


logger = logging.getLogger(__name__)
load_dotenv()


def download_extract_scheme(url: str, repo_name: str):
    os.makedirs("downloads", exist_ok=True)
    logger.info(f"Downloading scheme from {url}")
    try:
        response = urlopen(url)
        repo_zip = zipfile.ZipFile(BytesIO(response.read()))
        repo_zip.extractall("downloads/relying-party-repo")
        logger.info(
            f"Successfully extracted zip file to downloads/relying-party-repo/{repo_name}-master"
        )
    except Exception as e:
        logger.error(f"Error extracting the zip file: {e}")
        raise


def load_requestor_data(repo_folder: str):
    requestors_json_path = os.path.join(repo_folder, "requestors.json")
    if not os.path.exists(requestors_json_path):
        logger.error(f"requestors.json not found in {repo_folder}")
        raise FileNotFoundError(f"requestors.json not found in {repo_folder}")

    try:
        with open(requestors_json_path, "r", encoding="utf-8") as f:
            rp_list = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load requestors.json: {e}")
        raise

    logger.info(f"Found {len(rp_list)} verifiers in the JSON.")
    return rp_list


def fields_from_verifier(repo_folder: str, rp_data: dict):
    try:
        slug = rp_data["id"].split(".")[1]
        hostnames = rp_data.get("hostnames", [])
        name_en = rp_data.get("name", {}).get("en", slug)
        name_nl = rp_data.get("name", {}).get("nl", slug)
        logo_hash = rp_data.get("logo")
        logo_path = os.path.join(repo_folder, "assets", f"{logo_hash}.png")
        return slug, hostnames, name_en, name_nl, logo_path
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting fields from verifier: {e}")
        raise


def create_rp(
    org,
    yivi_tme,
    rp_data: dict,
    slug: str,
):
    if not org or not yivi_tme:
        raise ValueError("Missing organization or trust model environment")

    try:
        rp, rp_created = RelyingParty.objects.update_or_create(
            organization=org,
            yivi_tme=yivi_tme,
            defaults={
                "approved_rp_details": rp_data,
                "published_rp_details": rp_data,
            },
        )

        logger.info(f"{'Created' if rp_created else 'Updated'} Relying Party: {slug}")

    except Exception as rp_error:
        logger.error(f"Failed to create/update RelyingParty for {org}: {rp_error}")
        raise

    return rp


def create_hostnames(hostnames: str, rp: str, slug: str, environment: str):
    # validate if hostname object can be created
    if not rp:
        raise ValueError("Missing relying party object")
    if not hostnames:
        logger.error(f"No hostnames found for {slug}")
        raise ValueError(f"No hostnames found for {slug}")

    for hostname in hostnames:
        try:
            rp_hostname, hostname_created = (
                RelyingPartyHostname.objects.update_or_create(
                    relying_party=rp,
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
            raise


@transaction.atomic
def create_org_rp(repo_folder: str, environment: str):
    """
    For each verifier in the requestors json file, create or update the corresponding
    Organization, RelyingParty, and RelyingPartyHostname objects in the database.
    """
    rp_list = load_requestor_data(repo_folder)

    if not rp_list:
        logger.error("No requestors data loaded")
        raise ValueError("No requestors data loaded")

    logger.info(f"Found {len(rp_list)} verifiers in the JSON.")

    for rp_data in rp_list:
        slug, hostnames, name_en, name_nl, logo_path = fields_from_verifier(
            repo_folder, rp_data
        )

        org = import_utils.create_org(slug, name_en, name_nl, logo_path)
        yivi_tme = import_utils.get_trust_model_env(environment)
        rp = create_rp(org, yivi_tme, rp_data, slug)
        create_hostnames(hostnames, rp, slug, environment)


# download requestors repo
def import_rps():
    try:
        config = import_utils.load_config()
        environment = os.environ.get("RP_ENV")
        logger.info(f"Current RP_ENV value: {environment}")
        if environment in ["staging", "production"]:
            logger.info(f"Importing relying parties for environment: {environment}")
        else:
            logger.error(f"No specific environment specified. Got: '{environment}'")
            raise ValueError(f"No specific environment specified. Got: '{environment}'")

        repo_url = config["RP"]["environment"]["production"]["repo-url"]
        repo_name = config["RP"]["environment"]["production"]["name"]
        download_extract_scheme(repo_url, repo_name)

        repo_folder = f"downloads/relying-party-repo/{repo_name}-master"
        create_org_rp(repo_folder, environment)
        logger.info("Relying parties imported/updated successfully.")

    except Exception as e:
        logger.error(f"Failed to import relying parties: {e}")
        raise
