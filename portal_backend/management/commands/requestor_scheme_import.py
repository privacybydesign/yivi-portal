from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
import json
import os
import tempfile
import zipfile
from urllib.request import urlopen
from io import BytesIO
from ...models.models import (
    RelyingParty,
    Organization,
    RelyingPartyHostname,
    YiviTrustModelEnv,
    Status,
)
from django.db import transaction, IntegrityError
from PIL import Image


class Command(BaseCommand):
    help = "Import verifiers from requestors scheme"

    # create records in database

    @transaction.atomic
    def create_org_rp_hostname(
        self, slug, logo_image_file, hostname, name_en, name_nl, verifier
    ):
        """
        Create Organization, RelyingParty, RelyingPartyHostname, and Status records for a verifier.
        """

        if Organization.objects.filter(slug=slug).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Organization '{slug}' already exists. Skipping creation."
                )
            )
            return

        org = Organization(
            slug=slug,
            is_verified=True,
            logo=logo_image_file,
            name_en=name_en,
            name_nl=name_nl,
            registration_number="AUTO-GENERATED",
            address="AUTO-GENERATED",
        )
        org.save()
        self.stdout.write(f"Created Organization: {slug}")

        yivi_tme = YiviTrustModelEnv.objects.get(environment="production")
        rp = RelyingParty.objects.create(
            organization=org,
            yivi_tme=yivi_tme,
            approved_rp_details=verifier,
            published_rp_details=verifier,
        )
        rp.save()
        self.stdout.write(f"Created RelyingParty for Organization: {slug}")

        rp_hostname = RelyingPartyHostname.objects.create(
            relying_party=rp,
            hostname=hostname,
            manually_verified=True,
            dns_challenge=None,
            dns_challenge_created_at=None,
        )
        self.stdout.write(f"Created Hostname: {hostname}")

    # download requestors repo
    repo_url = "https://github.com/privacybydesign/pbdf-requestors/archive/refs/heads/master.zip"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("downloading requestors scheme..."))

        os.makedirs("requestors-repo", exist_ok=True)

        response = urlopen(self.repo_url)
        zip_file = zipfile.ZipFile(BytesIO(response.read()))
        try:
            zip_file.extractall("requestors-repo")
        except:
            self.stdout.write(self.style.ERROR("Error extracting the zip file"))

        self.stdout.write(
            self.style.SUCCESS("Requestors scheme downloaded successfully")
        )

        # read the requestors.json file
        with open(
            "requestors-repo/pbdf-requestors-master/requestors.json",
            "r",
            encoding="utf-8",
        ) as f:
            verifier_list = json.load(f)
            print(f"Found {len(verifier_list)} verifiers in the JSON.")

        for verifier in verifier_list:
            logo_hash = verifier.get("logo")
            if logo_hash is None:
                print(f"No logo found for {verifier['id']}")
                continue
            slug = verifier["id"].split(".")[1]
            hostname = verifier["hostnames"][0]
            name_en = verifier["name"]["en"]
            name_nl = verifier["name"]["nl"]
            logo_path = f"requestors-repo/pbdf-requestors-master/assets/{logo_hash}.png"
            with open(logo_path, "rb") as f:
                logo_image_file = ImageFile(f, name=f"{logo_hash}.png")
                self.create_org_rp_hostname(
                    slug,
                    logo_image_file,
                    hostname,
                    name_en,
                    name_nl,
                    verifier,
                )
                self.stdout.write(self.style.SUCCESS(f"Created verifier: {slug}"))
        self.stdout.write(self.style.SUCCESS("Import completed successfully"))
