from typing import List
from portal_backend.models.models import RelyingPartyHostname
from portal_backend.types import HostnameEntry


def validate_and_save(obj):
    """
    Calls full_clean and save on a model instance. Will raise ValidationError if validation fails.
    """
    obj.full_clean()
    obj.save()
    return obj


def hostname_exists(hostname: str) -> bool:
    """
    Returns True if a hostname exists in the DB, else False.
    """
    return RelyingPartyHostname.objects.filter(hostname=hostname).exists()


def extract_hostnames(entries: List[HostnameEntry]) -> List[str]:
    """
    Extracts non-empty hostname strings from entry dicts.
    """
    return [
        entry.get("hostname")
        for entry in entries
        if isinstance(entry, dict) and entry.get("hostname")
    ]
