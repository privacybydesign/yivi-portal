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


def download_extract_scheme(url: str):
    logger.info(f"Downloading scheme from {url}")
    try:
        response = urlopen(url)
        repo_zip = zipfile.ZipFile(BytesIO(response.read()))
        repo_zip.extractall("downloads/attestation-provider-repo")
        logger.info(
            "Successfully extracted zip file to downloads/attestation-provider-repo"
        )
        return True
    except Exception as e:
        logger.error(f"Error downloading or extracting the zip file: {e}")
        raise


def convert_xml_to_json(repo_name):
    try:
        os.makedirs("downloads", exist_ok=True)
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
                            abs_logo_path = os.path.abspath(
                                f"{base_path}/{dir}/logo.png"
                            )
                            all_APs_dict[dir]["logo_path"] = abs_logo_path
                        else:
                            logger.info(f"No logo found for {dir}")
                            raise Exception(f"No logo found for {dir}")

        with open("downloads/all-APs.json", "w", encoding="utf-8") as all_APs_json:
            all_APs_json.write(
                json.dumps(all_APs_dict, indent=4, sort_keys=True, ensure_ascii=False)
            )

        logger.info(f"Found {len(all_APs_dict)} attestation providers.")
        if len(all_APs_dict) == 0:
            raise Exception("No attestation providers found")
        return True
    except Exception as e:
        logger.error(f"Error converting XML to JSON: {e}")
        raise


def create_org(name_en, name_nl, slug, contact_url, logo_path):
    try:
        with open(logo_path, "rb") as logo_file:
            logo_image_file = ImageFile(logo_file, name=f"{slug}.png")
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

            logger.info(
                f"{'Created' if org_created else 'Updated'} Organization: {slug}"
            )

    except Exception as e:
        logger.error(f"Error creating organization {slug}: {e}")
        raise
    return org


def create_ap(
    org, yivi_tme, version, shortname_en, shortname_nl, contact_email, base_url, slug
):
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
            f"{'Created' if ap_created else 'Updated'} Attestation Provider: {slug}"
        )

        return ap
    except Exception as e:
        logger.error(f"Error creating attestation provider for {slug}: {e}")
        raise


def get_trust_model_env(environment: str):
    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment=environment)
        return yivi_tme
    except YiviTrustModelEnv.DoesNotExist:
        raise Exception(
            f"YiviTrustModelEnv for environment '{environment}' does not exist"
        )


def fields_from_issuer(all_APs_dict, AP):
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
        logger.error(f"Error extracting fields from issuer: {e}")
        raise


@transaction.atomic
def create_update_APs(environment: str):
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

            org = create_org(name_en, name_nl, slug, contact_url, logo_path)

            create_ap(
                org,
                yivi_tme,
                version,
                shortname_en,
                shortname_nl,
                contact_email,
                base_url,
                slug,
            )

        logger.info(f"Found {len(all_APs_dict)} attestation providers in the JSON.")
        return True


def import_aps(config_file="config.json"):
    """Main function to import attestation providers"""
    try:
        load_dotenv()
        config = load_config(config_file)
        environment = os.environ.get("AP_ENV")
        if environment not in ["production", "staging", "demo"]:
            logger.error("No specific environment specified.")
            print(environment)
            return

        repo_url = config["AP"]["environment"][environment]["repo-url"]
        repo_name = config["AP"]["environment"][environment]["name"]
        download_extract_scheme(repo_url)
        convert_xml_to_json(repo_name)
        create_update_APs(environment)
        logger.info("Attestation providers imported/updated successfully.")

    except Exception as e:
        logger.error(f"Failed to import attestation providers: {e}")
        raise
