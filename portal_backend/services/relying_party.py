from typing import List, Dict
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
    hostnames: HostnameEntry, current_rp: RelyingParty
) -> List[str]:
    filtered = [h for h in hostnames if h]
    new_hostnames = [
        h.get("hostname") for h in filtered if isinstance(h, dict) and h.get("hostname")
    ]
    check_duplicate_hostnames(new_hostnames, current_rp=current_rp)
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
    data: HostnameEntry, relying_party: RelyingParty
) -> List[RelyingPartyHostname]:
    hostnames = data.get("hostnames", [])
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


# data: {'rp_slug': 'test-rp5', 'environment': 'demo', 'context_description_en': 'dfx', 'context_description_nl': 'fds',
# 'hostnames': ['verifier.example.nl'], 'attributes':
# [{'credential_attribute_name': 'pbdf.pbdf.email.email', 'reason_en': 'something new now', 'reason_nl': ' te sturen'}]}
def create_condiscon(
    data: RelyingPartyResponse, relying_party: RelyingParty
) -> Condiscon:
    print(f"data: {data}")

    condiscon_json = make_condiscon_json(data.get("attributes", []))
    condiscon = Condiscon.objects.create(
        condiscon=condiscon_json,
        relying_party=relying_party,
        context_description_en=data.get("context_description_en"),
        context_description_nl=data.get("context_description_nl"),
    )
    return condiscon


def create_condiscon_attributes(
    condiscon: Condiscon,
    attributes_data: List[
        AttributeEntry
    ],  # TODO: maybe it would be nicer to create a type model for this
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
    hostnames: List[HostnameEntry],
    response: Dict[str, str],
) -> None:
    new_hostnames = parse_and_validate_hostnames(hostnames, current_rp=relying_party)

    RelyingPartyHostname.objects.filter(relying_party=relying_party).delete()
    created = create_hostname_objects(new_hostnames, relying_party)

    response["hostnames"] = [
        {"hostname": h.hostname, "dns_challenge": h.dns_challenge} for h in created
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
    new_slug: str,
    response: Dict[str, str | list[dict[str, str]]],
) -> None:
    if new_slug != relying_party.rp_slug:
        relying_party.rp_slug = new_slug
        relying_party.save()
        response["rp_slug"] = relying_party.rp_slug
