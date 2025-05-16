from typing import List
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models.models import (
    Organization,
    RelyingParty,
    RelyingPartyHostname,
    YiviTrustModelEnv,
    Condiscon,
    CondisconAttribute,
    CredentialAttribute,
)
from ..dns_verification import generate_dns_challenge
from ..types import (
    HostnameEntry,
    AttributeEntry,
    CredentialAttributesEntry,
    CondisconJSON,
    RelyingPartyResponse,
)


def create_relying_party(
    data: RelyingPartyResponse, org_slug: str, rp_slug: str
) -> RelyingParty:
    organization = get_object_or_404(Organization, slug=org_slug)
    yivi_tme = get_object_or_404(
        YiviTrustModelEnv,
        environment=data.get("environment"),
        trust_model__name="yivi",
    )
    relying_party = RelyingParty(
        rp_slug=rp_slug,
        organization=organization,
        yivi_tme=yivi_tme,
        ready=False,
        reviewed_accepted=False,
        reviewed_at=None,
        rejection_remarks=None,
        published_at=None,
    )
    relying_party.full_clean()
    relying_party.save()
    return relying_party


def check_duplicate_hostnames(
    hostnames: List[str],
) -> None:
    """
    Raises ValidationError if any of the hostnames already exists in the database.
    """
    filtered = [h for h in hostnames if h]

    same_entries = RelyingPartyHostname.objects.filter(hostname__in=filtered)

    if same_entries.exists():
        raise ValidationError(
            {
                "hostnames": [
                    f"Hostname already exists: {h.hostname}" for h in same_entries
                ]
            }
        )


def parse_and_validate_hostnames(
    hostnames: HostnameEntry,
) -> List[str]:
    filtered = [h for h in hostnames if h]
    new_hostnames = [
        h.get("hostname") for h in filtered if isinstance(h, dict) and h.get("hostname")
    ]
    check_duplicate_hostnames(new_hostnames)
    return new_hostnames


def create_hostname_objects(
    hostnames: List[str], relying_party: RelyingParty
) -> List[RelyingPartyHostname]:
    created = []
    for hostname in hostnames:
        obj = RelyingPartyHostname.objects.create(
            relying_party=relying_party,
            hostname=hostname,
            dns_challenge=generate_dns_challenge(),
            dns_challenge_created_at=timezone.now(),
            dns_challenge_verified=False,
        )
        obj.full_clean()
        obj.save()
        created.append(obj)
    return created


def create_hostnames(
    hostnames: List[HostnameEntry], relying_party: RelyingParty
) -> List[RelyingPartyHostname]:
    new_hostnames = parse_and_validate_hostnames(hostnames)
    return create_hostname_objects(new_hostnames, relying_party)


# TODO: right now we are making a condiscon with OR for each credential type, we will need a more advanced
# condiscon maker that can handle full possibilities of the condiscon supported by the frontend
def make_condiscon_json(
    attributes_data: List[AttributeEntry],
) -> CondisconJSON:
    condiscon_json = {
        "@context": "https://irma.app/ld/request/disclosure/v2",
        "disclose": [],
    }
    credential_attributes: CredentialAttributesEntry = {}

    for attr in attributes_data:
        cred_attr = get_object_or_404(
            CredentialAttribute, name=attr["credential_attribute_name"]
        )
        cred_id = cred_attr.credential.id
        credential_attributes.setdefault(cred_id, []).append(cred_attr.name)

    for attr_list in credential_attributes.values():
        condiscon_json["disclose"].append([attr_list])

    return condiscon_json


def create_condiscon(
    attributes: List[AttributeEntry],
    contexts: dict[str, str],
    relying_party: RelyingParty,
) -> Condiscon:

    condiscon_json = make_condiscon_json(attributes)
    condiscon = Condiscon.objects.create(
        condiscon=condiscon_json,
        relying_party=relying_party,
        context_description_en=contexts["en"],
        context_description_nl=contexts["nl"],
    )
    return condiscon


def create_condiscon_attributes(
    condiscon: Condiscon,
    attributes_data: List[AttributeEntry],
) -> None:
    for attr in attributes_data:
        cred_attr = get_object_or_404(
            CredentialAttribute, name=attr["credential_attribute_name"]
        )
        CondisconAttribute.objects.create(
            credential_attribute=cred_attr,
            condiscon=condiscon,
            reason_en=attr["reason_en"],
            reason_nl=attr["reason_nl"],
        )


def update_relying_party_hostnames(
    relying_party: RelyingParty,
    submitted_hostnames: List[HostnameEntry],
) -> List[dict[str, str]]:
    existing_hostnames = RelyingPartyHostname.objects.filter(
        relying_party=relying_party
    )
    hostnames_with_id = {str(h.id): h for h in existing_hostnames}
    update_or_add = []

    for entry in submitted_hostnames:
        hostname_str = entry.get("hostname", "").strip()
        if not hostname_str:
            continue

        hostname_id = entry.get("id", "")
        if str(hostname_id) in hostnames_with_id:
            hostname_obj = hostnames_with_id.pop(str(hostname_id))
            if hostname_obj.hostname != hostname_str:
                hostname_obj.hostname = hostname_str
                hostname_obj.dns_challenge = generate_dns_challenge()
                hostname_obj.manually_verified = False
                hostname_obj.dns_challenge_created_at = timezone.now()
                hostname_obj.dns_challenge_verified = False
                hostname_obj.full_clean()
                hostname_obj.save()
            update_or_add.append(hostname_obj)
        else:
            new_obj = RelyingPartyHostname.objects.create(
                relying_party=relying_party,
                hostname=hostname_str,
                dns_challenge=generate_dns_challenge(),
                dns_challenge_created_at=timezone.now(),
                dns_challenge_verified=False,
            )
            new_obj.full_clean()
            new_obj.save()
            update_or_add.append(new_obj)

    # delete remaining hostnames not in the submitted list
    for h in hostnames_with_id.values():
        h.delete()

    # return DNS challenges for the hostnames that were updated or added
    return [
        {"hostname": h.hostname, "dns_challenge": h.dns_challenge}
        for h in update_or_add
    ]


def update_condiscon_attributes(
    condiscon: Condiscon, attributes_data: List[AttributeEntry]
) -> None:
    CondisconAttribute.objects.filter(condiscon=condiscon).delete()
    create_condiscon_attributes(condiscon, attributes_data)


def update_condiscon_context(condiscon: Condiscon, data: RelyingPartyResponse) -> None:
    if "context_description_en" in data:
        condiscon.context_description_en = data["context_description_en"]
    if "context_description_nl" in data:
        condiscon.context_description_nl = data["context_description_nl"]
    condiscon.save()


def update_rp_environment(relying_party: RelyingParty, environment: str) -> None:
    yivi_tme = get_object_or_404(YiviTrustModelEnv, environment=environment)
    relying_party.yivi_tme = yivi_tme
    relying_party.save()


def update_rp_slug(
    relying_party: RelyingParty,
    updated_slug: str,
) -> None | str:
    if updated_slug != relying_party.rp_slug:
        relying_party.rp_slug = updated_slug
        relying_party.save()
        return updated_slug
    return None
