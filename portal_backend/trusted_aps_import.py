import zipfile
import xmltodict  # type: ignore
import json
from django.core.files.images import ImageFile
from io import BytesIO
import os
from dotenv import load_dotenv
from urllib.request import urlopen
from portal_backend.models.models import (
    Organization,
    YiviTrustModelEnv,
    AttestationProvider,
)
from django.db import transaction
import logging


logger = logging.getLogger(__name__)
os.makedirs("downloads", exist_ok=True)
os.makedirs("downloads/attestation-provider-repo", exist_ok=True)


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


def download_extract_scheme(url):
    logger.info(f"Downloading schema from {url}")
    response = urlopen(url)
    repo_zip = zipfile.ZipFile(BytesIO(response.read()))
    try:
        repo_zip.extractall("downloads/attestation-provider-repo")
        logger.info(
            "Successfully extracted zip file to downloads/attestation-provider-repo"
        )
    except Exception as e:
        logger.error(f"Error extracting the zip file: {e}")


def convert_xml_to_json(repo_name):
    os.makedirs("downloads", exist_ok=True)
    # go in each directory, find the description.xml file, convert it to json add it
    # to main dict with same key as directory name
    all_APs_json = open("downloads/all-APs.json", "w", encoding="utf-8")
    all_APs_dict = {}
    base_path = f"downloads/attestation-provider-repo/{repo_name}-master"

    logger.info(f"Looking for attestation providers in {base_path}")
    for root, dirs, files in os.walk(base_path):
        for dir in dirs:
            AP_xml_path = f"{base_path}/{dir}/description.xml"
            is_description_file_here = os.path.isfile(AP_xml_path)
            if is_description_file_here:
                logger.debug(f"Found description.xml for AP {dir}")
                with open(AP_xml_path) as f:
                    dict_data = xmltodict.parse(f.read())
                    all_APs_dict[dir] = dict_data

                    is_logo_here = os.path.isfile(f"{base_path}/{dir}/logo.png")
                    if is_logo_here:
                        abs_logo_path = os.path.abspath(f"{base_path}/{dir}/logo.png")
                        all_APs_dict[dir]["logo_path"] = abs_logo_path
                    else:
                        logger.info(f"No logo found for {dir}")

    all_APs_json.write(
        json.dumps(all_APs_dict, indent=4, sort_keys=True, ensure_ascii=False)
    )
    all_APs_json.close()
    logger.info(f"Found {len(all_APs_dict)} attestation providers.")


@transaction.atomic
def create_update_APs(environment):
    with open("downloads/all-APs.json", "r", encoding="utf-8") as f:
        all_APs_dict = json.load(f)

        for AP in all_APs_dict:
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

            try:
                yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
            except YiviTrustModelEnv.DoesNotExist:
                logger.error(
                    f"YiviTrustModelEnv for environment '{environment}' does not exist!"
                )
                return

            with open(logo_path, "rb") as f:
                logo_image_file = ImageFile(f, name=f"{slug}.png")
                org, org_created = Organization.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name_en": name_en,
                        "name_nl": name_nl,
                        "slug": slug,
                        "logo": logo_image_file,
                        "registration_number": "AUTO-GENERATED",
                        "contact_address": contact_url,
                        "is_verified": True,
                    },
                )
                if org_created:
                    logger.info(f"Created Organization: {slug}")
                else:
                    logger.info(f"Updated Organization: {slug}")

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
                if ap_created:
                    logger.info(f"Created Attestation Provider: {slug}")
                else:
                    logger.info(f"Updated Attestation Provider: {slug}")

        logger.info(f"Found {len(all_APs_dict)} attestation providers in the JSON.")


def import_aps(config_file="config.json"):
    """Main function to import attestation providers"""
    load_dotenv()

    config = load_config(config_file)
    if os.environ.get("AP_ENV") == "production":
        repo_url = config["AP"]["environment"]["production"]["repo-url"]
        repo_name = config["AP"]["environment"]["production"]["name"]
        environment = "production"
    elif os.environ.get("AP_ENV") == "staging":
        repo_url = config["AP"]["environment"]["staging"]["repo-url"]
        repo_name = config["AP"]["environment"]["staging"]["name"]
        environment = "staging"
    elif os.environ.get("AP_ENV") == "demo":
        repo_url = config["AP"]["environment"]["demo"]["repo-url"]
        repo_name = config["AP"]["environment"]["demo"]["name"]
        environment = "demo"
    else:
        logger.error("No specific environment specified.")
        print(os.environ.get("AP_ENV"))
        return

    download_extract_scheme(repo_url)
    convert_xml_to_json(repo_name)
    create_update_APs(environment)
    logger.info("Attestation providers imported/updated successfully.")
