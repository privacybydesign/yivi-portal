import requests
import zipfile
from django.core.management.base import BaseCommand
import xmltodict  # type: ignore
import json
from django.core.files.images import ImageFile
from io import BytesIO
import os
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


def download_extract_scheme():

    url = "https://github.com/privacybydesign/pbdf-schememanager/archive/refs/heads/master.zip"
    response = urlopen(url)
    zip_file = zipfile.ZipFile(BytesIO(response.read()))
    try:
        zip_file.extractall("downloads/attestation-provider-repo")
    except Exception as e:
        logger.error(f"Error extracting the zip file: {e}")


def convert_xml_to_json():
    os.makedirs("downloads", exist_ok=True)
    # go in each directory, find the description.xml file, convert it to json add it
    # to main dict with same key as directory name
    all_APs_json = open("downloads/all-APs.json", "w", encoding="utf-8")
    all_APs_dict = {}
    for root, dirs, files in os.walk(
        "downloads/attestation-provider-repo/pbdf-schememanager-master"
    ):
        for dir in dirs:
            AP_xml_path = f"downloads/attestation-provider-repo/pbdf-schememanager-master/{dir}/description.xml"
            is_description_file_here = os.path.isfile(AP_xml_path)
            if is_description_file_here:
                logger.debug(f"Found description.xml for AP {dir}")
                with open(AP_xml_path) as f:
                    dict_data = xmltodict.parse(f.read())
                    all_APs_dict[dir] = dict_data

                    is_logo_here = os.path.isfile(
                        f"downloads/attestation-provider-repo/pbdf-schememanager-master/{dir}/logo.png"
                    )
                    if is_logo_here:
                        abs_logo_path = os.path.abspath(
                            f"downloads/attestation-provider-repo/pbdf-schememanager-master/{dir}/logo.png"
                        )
                        all_APs_dict[dir]["logo_path"] = abs_logo_path
                    else:
                        logger.info(f"No logo found for {dir}")

    all_APs_json.write(
        json.dumps(all_APs_dict, indent=4, sort_keys=True, ensure_ascii=False)
    )
    all_APs_json.close()


@transaction.atomic
def create_update_APs():
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

                yivi_tme = YiviTrustModelEnv.objects.get(environment="production")
                ap, ap_created = AttestationProvider.objects.get_or_create(
                    organization=org,
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


def import_aps():
    download_extract_scheme()
    convert_xml_to_json()
    create_update_APs()
    logger.info("Attestation providers imported/updated successfully.")
