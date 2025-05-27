import xmltodict  # type: ignore
import json
import os
from dotenv import load_dotenv  # type: ignore
from portal_backend.models.models import (
    TrustModel,
    YiviTrustModelEnv,
    AttestationProvider,
    Credential,
    CredentialAttribute,
)
from django.db import transaction
import logging
import portal_backend.scheme_utils.import_utils as import_utils
from django.utils import timezone
from datetime import datetime


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

    issues_dir = os.path.join(repo_path, ap_dir, "Issues")
    if not os.path.isdir(issues_dir):
        issues_dir = os.path.join(repo_path, ap_dir, "issues")

    credentials = {}
    if os.path.isdir(issues_dir):
        for cred_id in os.listdir(issues_dir):
            cred_desc = os.path.join(issues_dir, cred_id, "description.xml")
            if not os.path.isfile(cred_desc):
                continue
            with open(cred_desc) as cred_file:
                credentials[cred_id] = xmltodict.parse(cred_file.read())
    ap_data["credentials"] = credentials

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
            self.contact_address = self.all_APs_dict[self.AP]["Issuer"][
                "ContactAddress"
            ]
            self.logo_path = self.all_APs_dict[self.AP]["logo_path"]
            self.base_url = self.all_APs_dict[self.AP]["Issuer"].get("baseURL")
            self.credentials = self.all_APs_dict[self.AP].get("credentials", {})

        except Exception as e:
            raise Exception(f"Error extracting fields from issuer: {e}")


class CredentialFields:
    def __init__(self, credential_dict: dict) -> None:
        try:
            spec = credential_dict.get("IssueSpecification", {})
            self.credential_id = spec.get("CredentialID")
            name = spec.get("Name", {})
            self.name_en = name.get("en")
            self.name_nl = name.get("nl")
            shortname = spec.get("ShortName", {})
            self.shortname_en = shortname.get("en")
            self.shortname_nl = shortname.get("nl")
            self.description_en = spec.get("Description", {}).get("en")
            self.description_nl = spec.get("Description", {}).get("nl")
            self.should_be_singleton = (
                spec.get("ShouldBeSingleton", "").lower() == "true"
            )
            self.issue_url = None
            issue_url = spec.get("IssueURL")
            if isinstance(issue_url, dict):
                self.issue_url = issue_url.get("en") or issue_url.get("nl")
            else:
                self.issue_url = issue_url

            # Convert DeprecatedSince from UNIX Timestamp to date format
            deprecated_raw = spec.get("DeprecatedSince")
            if deprecated_raw:
                try:
                    if deprecated_raw.isdigit():  # Unix timestamp
                        dt = datetime.utcfromtimestamp(int(deprecated_raw))
                        self.deprecated_since = dt.date().isoformat()  # 'YYYY-MM-DD'
                    else:
                        self.deprecated_since = deprecated_raw  # assume valid date
                except Exception as e:
                    raise Exception(f"Invalid DeprecatedSince value: {e}")
            else:
                self.deprecated_since = None

            attributes = spec.get("Attributes", {}).get("Attribute", [])

            if isinstance(attributes, list):
                self.attributes = attributes
            else:
                self.attributes = [attributes]
        except Exception as e:
            raise Exception(f"Error extracting fields from credential: {e}")


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
                "contact_address": apfields.contact_address,
                "base_url": apfields.base_url,
                "ready": True,
                "reviewed_accepted": True,
                "published": True,
                "ap_slug": apfields.slug,
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


def create_credential(
    ap: AttestationProvider, cfields: CredentialFields, environment: str
) -> Credential:
    try:
        credential, created = Credential.objects.update_or_create(
            attestation_provider=ap,
            credential_id=cfields.credential_id,
            defaults={
                "name_en": cfields.name_en,
                "name_nl": cfields.name_nl,
                "shortname_en": cfields.shortname_en,
                "shortname_nl": cfields.shortname_nl,
                "description_en": cfields.description_en,
                "description_nl": cfields.description_nl,
                "issue_url": cfields.issue_url,
                "should_be_singleton": cfields.should_be_singleton,
                "deprecated_since": cfields.deprecated_since,
            },
        )

        logger.info(
            f"{'Created' if created else 'Updated'} Credential {cfields.credential_id} for AP {ap.organization.slug} in environment {environment}"
        )

        return credential
    except Exception as e:
        raise Exception(f"Error creating credential {cfields.credential_id}: {e}")


def create_credential_attributes(
    credential: Credential, cfields: CredentialFields, environment: str
) -> None:
    for attr in cfields.attributes:
        try:
            if not attr.get("Name"):  # Skipping incomplete attributes
                logger.warning(
                    f"Skipping unnamed attribute in credential {credential.credential_id}"
                )
                continue

            name = attr.get("Name", {})
            desc = attr.get("Description", {})

            CredentialAttribute.objects.update_or_create(
                credential=credential,
                name_en=name.get("en"),
                defaults={
                    "credential_attribute_id": attr.get("@id"),
                    "name_nl": name.get("nl"),
                    "description_en": desc.get("en"),
                    "description_nl": desc.get("nl"),
                },
            )
        except Exception as e:
            raise Exception(
                f"Error creating attribute for credential {credential.credential_id}: {e}"
            )


def get_scheme_description(scheme_description_xml: str) -> dict:
    try:
        with open(scheme_description_xml, "r", encoding="utf-8") as f:
            return xmltodict.parse(f.read())
    except Exception as e:
        raise Exception(
            f"Failed to parse scheme description at {scheme_description_xml}: {e}"
        )


def create_update_trust_model_env(
    environment: str,
    data: dict,
) -> YiviTrustModelEnv:
    try:
        scheme = data.get("SchemeManager", {})

        if not scheme:
            raise ValueError("Missing 'SchemeManager' in scheme description data")
        trust_model = TrustModel.objects.get(name__iexact="yivi")

        if not trust_model:
            raise ValueError("TrustModel 'yivi' does not exist in the database")

        yivi_tme, created = YiviTrustModelEnv.objects.update_or_create(
            trust_model=trust_model,
            environment=environment,
            defaults={
                "version": scheme.get("@version"),
                "scheme_id": scheme.get("Id"),
                "url": scheme.get("Url"),
                "name_en": scheme.get("Name").get("en"),
                "name_nl": scheme.get("Name").get("nl"),
                "description_en": scheme.get("Description").get("en"),
                "description_nl": scheme.get("Description").get("nl"),
                "minimum_android_version": scheme.get("MinimumAppVersion").get(
                    "Android"
                ),
                "minimum_ios_version": scheme.get("MinimumAppVersion").get("iOS"),
                "keyshare_server": scheme.get("KeyshareServer"),
                "keyshare_website": scheme.get("KeyshareWebsite"),
                "keyshare_attribute": scheme.get("KeyshareAttribute"),
                "timestamp_server": scheme.get("TimestampServer"),
                "contact_website": scheme.get("Contact"),
            },
        )

        logger.info(
            f"{'Created' if created else 'Updated'} YiviTrustModelEnv for {environment}"
        )
        return yivi_tme

    except Exception as e:
        raise Exception(f"Failed to create/update YiviTrustModelEnv: {e}")


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

            ap = create_ap(
                org,
                yivi_tme,
                apfields,
                environment=environment,
            )

            for cred_id, cred_dict in apfields.credentials.items():
                cfields = CredentialFields(cred_dict)
                credential = create_credential(ap, cfields, environment)
                create_credential_attributes(credential, cfields, environment)

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
        scheme_desc = get_scheme_description(
            REPO_DIR + f"/{repo_name}-master/description.xml"
        )
        create_update_trust_model_env(
            environment,
            scheme_desc,
        )

    except Exception as e:
        raise Exception(f"Failed to import Attestation Providers: {e}")
