from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
import json
import os
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
# create records in database


@transaction.atomic
def create_org_rp_hostname(
    slug, logo_image_file, hostnames, name_en, name_nl, verifier
):
    """
    Create Organization, RelyingParty, RelyingPartyHostname, and Status records for a verifier.
    """

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

    if org_created:
        logger.info(f"Created Organization: {slug}")

    else:
        logger.info(f"Updated Organization: {slug}")

    yivi_tme = YiviTrustModelEnv.objects.get(environment="production")
    rp, rp_created = RelyingParty.objects.update_or_create(
        organization=org,
        defaults={
            "yivi_tme": yivi_tme,
            "approved_rp_details": verifier,
            "published_rp_details": verifier,
        },
    )

    if rp_created:
        logger.info(f"Created RelyingParty for Organization: {slug}")
    else:
        logger.info(f"Updated RelyingParty for Organization: {slug}")
    for i in range(0, hostnames.__len__()):
        hostname = hostnames[i]
        rp_hostname, hostname_created = RelyingPartyHostname.objects.update_or_create(
            relying_party=rp,
            hostname=hostname,
            defaults={
                "manually_verified": True,
                "dns_challenge": None,
                "dns_challenge_created_at": None,
            },
        )

        if hostname_created:
            logger.info(f"Created Hostname: {hostname}")
        else:
            logger.info(f"Updated Hostname: {hostname}")


# download requestors repo
def import_rps():

    repo_url = "https://github.com/privacybydesign/pbdf-requestors/archive/refs/heads/master.zip"

    logger.info("downloading requestors scheme...")
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("downloads/requestors-repo", exist_ok=True)

    response = urlopen(repo_url)
    zip_file = zipfile.ZipFile(BytesIO(response.read()))
    try:
        zip_file.extractall("downloads/requestors-repo")
    except Exception as e:
        logger.error(f"Error extracting the zip file: {e}")

    logger.info("Requestors scheme downloaded successfully")

    # read the requestors.json file
    with open(
        "downloads/requestors-repo/pbdf-requestors-master/requestors.json",
        "r",
        encoding="utf-8",
    ) as f:
        verifier_list = json.load(f)
        logger.debug(f"Found {len(verifier_list)} verifiers in the JSON.")

    for verifier in verifier_list:
        logo_hash = verifier.get("logo")
        if logo_hash is None:
            logger.info(f"No logo found for {verifier['id']}")
            continue
        slug = verifier["id"].split(".")[1]
        hostnames = verifier["hostnames"]
        name_en = verifier["name"]["en"]
        name_nl = verifier["name"]["nl"]
        logo_path = (
            f"downloads/requestors-repo/pbdf-requestors-master/assets/{logo_hash}.png"
        )
        with open(logo_path, "rb") as f:
            logo_image_file = ImageFile(f, name=f"{logo_hash}.png")
            create_org_rp_hostname(
                slug,
                logo_image_file,
                hostnames,
                name_en,
                name_nl,
                verifier,
            )
    logger.info("Import completed successfully")
