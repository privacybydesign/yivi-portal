import zipfile
import xmltodict  # type: ignore
import json
from io import BytesIO
import os
from dotenv import load_dotenv
from urllib.request import urlopen
from portal_backend.models.models import (
    YiviTrustModelEnv,
    AttestationProvider,
)
from django.db import transaction
import logging
import portal_backend.import_schemes.import_utils as import_utils


logger = logging.getLogger(__name__)
os.makedirs("downloads", exist_ok=True)
os.makedirs("downloads/attestation-provider-repo", exist_ok=True)


def download_extract_scheme(url: str) -> None:
    """Download and extract the zip of Attestation Provider Github repository"""
    logger.info(f"Downloading scheme from {url}")
    try:
        response = urlopen(url)
        repo_zip = zipfile.ZipFile(BytesIO(response.read()))
        repo_zip.extractall("downloads/attestation-provider-repo")
        logger.info(
            "Successfully extracted zip file to downloads/attestation-provider-repo"
        )
    except Exception as e:
        logger.error(f"Error downloading or extracting the zip file: {e}")
        raise


def convert_xml_to_json(repo_name: str) -> None:
    """Convert all XML files in the Attestation Provider directories to JSON"""
    try:
        os.makedirs("downloads", exist_ok=True)
        all_APs_dict = {}
        base_path = f"downloads/attestation-provider-repo/{repo_name}-master"

        logger.info(f"Looking for Attestation Providers in {base_path}")

        for ap_dir in find_ap_directories(base_path):
            ap_data = process_ap_directory(base_path, ap_dir)
            if ap_data:
                all_APs_dict[ap_dir] = ap_data

        write_aps_to_json(all_APs_dict)

        if not all_APs_dict:
            raise Exception("No Attestation Providers found")

        logger.info(f"Found {len(all_APs_dict)} Attestation Providers.")

    except Exception as e:
        raise Exception(f"Error converting XML to JSON: {e}")


def find_ap_directories(base_path: str) -> list[str]:
    """Return a list of Attestation Provider directories"""
    directories = []
    for _, dirs, _ in os.walk(base_path):
        directories.extend(dirs)
        break  # only top-level directories
    return directories


def process_ap_directory(base_path: str, ap_dir: str) -> dict | None:
    """Forming all Attestation Provider details in a directory into a dictionary"""
    AP_xml_path = f"{base_path}/{ap_dir}/description.xml"

    if not os.path.isfile(AP_xml_path):
        return None

    logger.debug(f"Found description.xml for AP {ap_dir}")

    with open(AP_xml_path) as f:
        ap_data = xmltodict.parse(f.read())

    logo_path = f"{base_path}/{ap_dir}/logo.png"
    if not os.path.isfile(logo_path):
        logger.info(f"No logo found for {ap_dir}")
        raise Exception(f"No logo found for {ap_dir}")

    ap_data["logo_path"] = os.path.abspath(logo_path)
    return ap_data


def write_aps_to_json(all_APs_dict: dict) -> None:
    """Write the Attestation Provider details to a JSON file."""
    with open("downloads/all-APs.json", "w", encoding="utf-8") as all_APs_json:
        all_APs_json.write(
            json.dumps(all_APs_dict, indent=4, sort_keys=True, ensure_ascii=False)
        )


def create_ap(
    org: import_utils.Organization,
    yivi_tme: import_utils.YiviTrustModelEnv,
    version,
    shortname_en,
    shortname_nl,
    contact_email,
    base_url,
    slug,
    environment,
) -> AttestationProvider:
    """Create or update an Attestation Provider in the database"""
    try:
        ap, ap_created = AttestationProvider.objects.get_or_create(
            organization=org,
            yivi_tme=yivi_tme,
            defaults={
                "yivi_tme": yivi_tme,
                "organization": org,
                "version": version,
                "shortname_en": shortname_en,
                "shortname_nl": shortname_nl,
                "contact_email": contact_email,
                "base_url": base_url,
            },
        )

        logger.info(
            f"{'Created' if ap_created else 'Updated'} Attestation Provider: {slug} in environment {environment}"
        )

        return ap
    except Exception as e:
        raise Exception(f"Error creating Attestation Provider for {slug}: {e}")


def get_trust_model_env(environment: str) -> YiviTrustModelEnv:
    """Get the YiviTrustModelEnv object for the specified environment, so we can link the Attestation Providers to it"""
    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
        return yivi_tme
    except YiviTrustModelEnv.DoesNotExist:
        raise Exception(
            f"YiviTrustModelEnv for environment '{environment}' does not exist"
        )


def fields_from_issuer(
    all_APs_dict: dict, AP: str
) -> tuple[str, str, str, str, str, str, str, str, str, str]:
    """Extract the fields from the Issuer dictionary in the JSON"""
    try:
        slug = AP
        version = all_APs_dict[AP]["Issuer"]["@version"]
        name_en = all_APs_dict[AP]["Issuer"]["Name"]["en"]
        name_nl = all_APs_dict[AP]["Issuer"]["Name"]["nl"]
        shortname_en = all_APs_dict[AP]["Issuer"]["ShortName"]["en"]
        shortname_nl = all_APs_dict[AP]["Issuer"]["ShortName"]["nl"]
        contact_url = all_APs_dict[AP]["Issuer"]["ContactAddress"]
        contact_email = all_APs_dict[AP]["Issuer"]["ContactEMail"]
        logo_path = all_APs_dict[AP]["logo_path"]
        base_url = all_APs_dict[AP]["Issuer"].get("baseURL")
        return (
            slug,
            version,
            name_en,
            name_nl,
            shortname_en,
            shortname_nl,
            contact_url,
            contact_email,
            logo_path,
            base_url,
        )
    except Exception as e:
        raise Exception(f"Error extracting fields from issuer: {e}")


@transaction.atomic
def create_update_APs(environment: str) -> None:
    """For each Issuer in the JSON, create/update the corresponding Attestation Provider and Organization"""
    with open("downloads/all-APs.json", "r", encoding="utf-8") as f:
        all_APs_dict = json.load(f)

        yivi_tme = get_trust_model_env(environment)

        for AP in all_APs_dict:
            (
                slug,
                version,
                name_en,
                name_nl,
                shortname_en,
                shortname_nl,
                contact_url,
                contact_email,
                logo_path,
                base_url,
            ) = fields_from_issuer(all_APs_dict, AP)

            org = import_utils.create_org(slug, name_en, name_nl, logo_path)

            create_ap(
                org,
                yivi_tme,
                version,
                shortname_en,
                shortname_nl,
                contact_email,
                base_url,
                slug,
                environment,
            )

        logger.info(f"Found {len(all_APs_dict)} Attestation Providers in the JSON.")


def import_aps(config_file="config.json") -> None:
    """Main function to import Attestation Providers"""
    try:
        load_dotenv()
        config = import_utils.load_config(config_file)
        environment = os.environ.get("AP_ENV")
        if environment not in ["production", "staging", "demo"]:
            logger.error(f"No specific environment specified. Got: '{environment}'")
            raise ValueError("No specific environment specified.")

        repo_url = config["AP"]["environment"][environment]["repo-url"]
        repo_name = config["AP"]["environment"][environment]["name"]
        download_extract_scheme(repo_url)
        convert_xml_to_json(repo_name)
        create_update_APs(environment)

    except Exception as e:
        raise Exception(f"Failed to import Attestation Providers: {e}")
