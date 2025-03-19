import os
from dotenv import load_dotenv
from django.db import transaction
from portal_backend.models.models import (
    RelyingParty,
    RelyingPartyHostname,
)
import logging
import portal_backend.import_schemes.import_utils as import_utils


logger = logging.getLogger(__name__)
load_dotenv()

DOWNLOADS_DIR = "downloads"
EXTRACT_DIR = f"{DOWNLOADS_DIR}/relying-party-repo"

load_dotenv()

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


class RPFields:
    """
    Extracts the fields for a single RP from the JSON data.
    """

    def __init__(self, rp_dict: dict, repo_path: str) -> None:
        self.rp_dict = rp_dict
        self.repo_path = repo_path
        try:
            self.slug = self.rp_dict["id"].split(".")[1]
            self.hostnames = self.rp_dict.get("hostnames", [])
            self.name_en = self.rp_dict.get("name", {}).get("en", self.slug)
            self.name_nl = self.rp_dict.get("name", {}).get("nl", self.slug)
            self.logo_path = os.path.join(
                self.repo_path, "assets", f"{self.rp_dict.get('logo')}.png"
            )
        except (KeyError, IndexError) as e:
            raise Exception(f"Error extracting fields from verifier: {e}")


def create_rp(
    org: import_utils.Organization,
    yivi_tme: import_utils.YiviTrustModelEnv,
    rp_dict: dict,
    environment: str,
) -> RelyingParty:
    """
    Create or update a RelyingParty object in the database and return the object"""
    if not org or not yivi_tme:
        raise ValueError("Missing organization or trust model environment")

    try:
        rp, rp_created = RelyingParty.objects.update_or_create(
            organization=org,
            yivi_tme=yivi_tme,
            defaults={
                "approved_rp_details": rp_dict,
                "published_rp_details": rp_dict,
            },
        )

        logger.info(
            f"{'Created' if rp_created else 'Updated'} Relying Party: {org} in environment {environment}"
        )

    except Exception as rp_error:
        raise Exception(f"Failed to create/update RelyingParty for {org}: {rp_error}")

    return rp


def create_hostnames(
    rpfields: RPFields,
    rp: RelyingParty,
    environment: str,
) -> None:
    """
    Create or update RelyingPartyHostname objects for the RelyingParty object"""

    # validate if hostname object can be created
    if not rp:
        raise ValueError("Missing relying party object")
    if not rpfields.hostnames:
        raise ValueError(f"No hostnames found for {rpfields.slug}")

    for hostname in rpfields.hostnames:
        try:
            _, hostname_created = RelyingPartyHostname.objects.update_or_create(
                relying_party=rp,
                hostname=hostname,
                defaults={
                    "manually_verified": True,
                    "dns_challenge": None,
                    "dns_challenge_created_at": None,
                },
            )
            logger.info(
                f"{'Created' if hostname_created else 'Updated'} Hostname: {hostname} for RP {rpfields.slug} in environment {environment}"
            )
        except Exception as hostname_error:
            raise Exception(
                f"Failed to create/update Hostname {hostname} for RP {rpfields.slug}: {hostname_error}"
            )


@transaction.atomic
def create_org_rp(all_RPs_dict: dict, environment: str, repo_path: str) -> None:
    """
    For each Relying Party in the JSON file, create or update the corresponding
    Organization, RelyingParty, and RelyingPartyHostname objects in the database.
    """

    if not all_RPs_dict:
        raise ValueError("No requestors data loaded")

    logger.info(f"Found {len(all_RPs_dict)} verifiers in the JSON.")

    for rp_dict in all_RPs_dict:
        rpfields = RPFields(rp_dict, repo_path)
        org = import_utils.create_org(
            rpfields.slug, rpfields.name_en, rpfields.name_nl, rpfields.logo_path
        )
        print("logo_path", rpfields.logo_path)
        yivi_tme = import_utils.get_trust_model_env(environment)
        rp = create_rp(org, yivi_tme, rp_dict, environment)
        create_hostnames(rpfields, rp, environment)


# download requestors repo
def import_rps() -> None:

    try:
        config = import_utils.load_config()
        environment = os.environ.get("RP_ENV")

        if environment in ["staging", "production"]:
            logger.info(f"Importing relying parties for environment: {environment}")
        else:
            raise ValueError(f"No specific environment specified. Got: '{environment}'")

        repo_url = config["RP"]["environment"]["production"]["repo-url"]
        repo_name = config["RP"]["environment"]["production"]["name"]
        repo_path = f"{EXTRACT_DIR}/{repo_name}-master"

        import_utils.download_extract_repo(repo_url, repo_name, EXTRACT_DIR)

        all_RPs_dict = import_utils.load_json_to_dict(f"{repo_path}/requestors.json")
        create_org_rp(all_RPs_dict, environment, repo_path)

    except Exception as e:
        raise Exception(f"Failed to import relying parties: {e}")
