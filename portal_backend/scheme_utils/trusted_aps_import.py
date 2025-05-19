import xmltodict  # type: ignore
import json
import os
from dotenv import load_dotenv  # type: ignore
from portal_backend.models.models import (
    YiviTrustModelEnv,
    AttestationProvider,
)
from django.db import transaction
import logging
import portal_backend.scheme_utils.import_utils as import_utils
from django.utils import timezone


logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"
REPO_DIR = f"{DOWNLOADS_DIR}/attestation-provider-repo"
AP_JSON_PATH = f"{DOWNLOADS_DIR}/all-APs.json"
CONFIG_FILE = "/app/config.json"
load_dotenv()

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(REPO_DIR, exist_ok=True)


def convert_xml_to_json(repo_name: str) -> None:
    try:
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        all_APs_dict = {}
        repo_path = f"{REPO_DIR}/{repo_name}-master"

        logger.info(f"Looking for Attestation Providers in {repo_path}")

        for ap_dir in find_ap_directories(repo_path):
            ap_data = process_ap_directory(repo_path, ap_dir)
            if ap_data:
                all_APs_dict[ap_dir] = ap_data

        write_aps_to_json(all_APs_dict)

        if not all_APs_dict:
            raise Exception("No Attestation Providers found")

        logger.info(f"Found {len(all_APs_dict)} Attestation Providers.")

    except Exception as e:
        raise Exception(f"Error converting XML to JSON: {e}")


def find_ap_directories(repo_path: str) -> list[str]:
    directories = []
    for _, dirs, _ in os.walk(repo_path):
        directories.extend(dirs)
        break
    return directories


def process_ap_directory(repo_path: str, ap_dir: str) -> dict | None:
    ap_xml_path = f"{repo_path}/{ap_dir}/description.xml"

    if not os.path.isfile(ap_xml_path):
        return None

    logger.debug(f"Found description.xml for AP {ap_dir}")

    with open(ap_xml_path) as f:
        ap_data = xmltodict.parse(f.read())

    logo_path = f"{repo_path}/{ap_dir}/logo.png"
    if not os.path.isfile(logo_path):
        logger.info(f"No logo found for {ap_dir}")
        raise Exception(f"No logo found for {ap_dir}")

    ap_data["logo_path"] = os.path.abspath(logo_path)
    return ap_data


def write_aps_to_json(all_APs_dict: dict) -> None:
    with open(AP_JSON_PATH, "w", encoding="utf-8") as all_APs_json:
        all_APs_json.write(
            json.dumps(all_APs_dict, indent=4, sort_keys=True, ensure_ascii=False)
        )


class APFields:
    def __init__(self, all_APs_dict: dict, AP: str) -> None:
        self.all_APs_dict = all_APs_dict
        self.AP = AP

        try:
            self.slug = self.AP
            self.version = self.all_APs_dict[self.AP]["Issuer"]["@version"]
            self.name_en = self.all_APs_dict[self.AP]["Issuer"]["Name"]["en"]
            self.name_nl = self.all_APs_dict[self.AP]["Issuer"]["Name"]["nl"]
            self.shortname_en = self.all_APs_dict[self.AP]["Issuer"]["ShortName"]["en"]
            self.shortname_nl = self.all_APs_dict[self.AP]["Issuer"]["ShortName"]["nl"]
            self.contact_email = self.all_APs_dict[self.AP]["Issuer"]["ContactEMail"]
            self.logo_path = self.all_APs_dict[self.AP]["logo_path"]
            self.base_url = self.all_APs_dict[self.AP]["Issuer"].get("baseURL")

        except Exception as e:
            raise Exception(f"Error extracting fields from issuer: {e}")


def create_ap(
    org: import_utils.Organization,
    yivi_tme: import_utils.YiviTrustModelEnv,
    apfields: APFields,
    environment,
) -> AttestationProvider:
    try:
        ap, ap_created = AttestationProvider.objects.update_or_create(
            organization=org,
            yivi_tme=yivi_tme,
            defaults={
                "version": apfields.version,
                "shortname_en": apfields.shortname_en,
                "shortname_nl": apfields.shortname_nl,
                "contact_email": apfields.contact_email,
                "base_url": apfields.base_url,
                "ready": True,
                "reviewed_accepted": True,
                "published": True,
            },
        )

        if ap_created:
            ap.published_at = timezone.now()
            ap.ready_at = timezone.now()
            ap.reviewed_at = timezone.now()
            ap.created_at = timezone.now()
            ap.save()

        logger.info(
            f"{'Created' if ap_created else 'Updated'} Attestation Provider: {apfields.slug} in environment {environment}"
        )

        return ap
    except Exception as e:
        raise Exception(f"Error creating Attestation Provider for {apfields.slug}: {e}")


def get_trust_model_env(environment: str) -> YiviTrustModelEnv:
    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
        return yivi_tme
    except YiviTrustModelEnv.DoesNotExist:
        raise Exception(
            f"YiviTrustModelEnv for environment '{environment}' does not exist"
        )


@transaction.atomic
def create_update_APs(environment: str) -> None:
    with open(AP_JSON_PATH, "r", encoding="utf-8") as f:
        all_APs_dict = json.load(f)
        yivi_tme = get_trust_model_env(environment)

        for AP in all_APs_dict:
            apfields = APFields(all_APs_dict, AP)
            org = import_utils.create_org(
                slug=apfields.slug,
                name_en=apfields.name_en,
                name_nl=apfields.name_nl,
                logo_path=apfields.logo_path,
            )

            create_ap(
                org,
                yivi_tme,
                apfields,
                environment=environment,
            )

        logger.info(f"Found {len(all_APs_dict)} Attestation Providers in the JSON.")


def import_aps(config_file=CONFIG_FILE) -> None:
    try:
        load_dotenv()
        config = import_utils.load_config(config_file)
        environment = os.environ.get("AP_ENV")
        if environment not in ["production", "staging", "demo"]:
            logger.error(f"No specific environment specified. Got: '{environment}'")
            raise ValueError("No specific environment specified.")

        repo_url = config["AP"]["environment"][environment]["repo-url"]
        repo_name = config["AP"]["environment"][environment]["name"]
        import_utils.download_extract_repo(repo_url, repo_name, REPO_DIR)
        convert_xml_to_json(repo_name)
        create_update_APs(environment)

    except Exception as e:
        raise Exception(f"Failed to import Attestation Providers: {e}")
