import logging
from django.utils import timezone
from .import_utils import load_config, download_extract_repo, load_json_to_dict
from ..models.models import RelyingParty

logger = logging.getLogger(__name__)


def check_published_rps(rps_dict: dict) -> None:
    db_rps = RelyingParty.objects.all()
    for db_rp in db_rps:
        if db_rp.status != "published":  # exclude existing rps editing their rp
            continue
        if db_rp.rp_slug not in str(rps_dict):
            db_rp.published = False
            db_rp.reviewed_accepted = False
            db_rp.ready = False
            db_rp.save()
        else:
            db_rp.published = True
            db_rp.reviewed_accepted = True
            db_rp.ready = True
            db_rp.published_at = timezone.now()
            db_rp.save()


def check_published_cron() -> None:

    try:

        # load into dict
        config = load_config()
        repo_url = config["RP"]["repo-url"]
        repo_name = config["RP"]["name"]
        repo_path = "downloads/relying-party-repo"
        download_extract_repo(repo_url, repo_name, repo_path)
        json_path = f"{repo_path}/{repo_name}-master/requestors.json"
        rps_dict = load_json_to_dict(json_path)

        # check if if all rps in the db are in the json and update their status
        check_published_rps(rps_dict)

    except Exception as e:
        raise Exception(f"Failed to check published Relying Parties: {e}")
