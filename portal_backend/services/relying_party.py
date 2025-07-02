from typing import List
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError

from portal_backend.services.helpers import (
    extract_hostnames,
    hostname_exists,
    validate_and_save,
)

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
        environment="production",  # setting production as default since the demo environment for requestors is totally different format
        trust_model__name__iexact="yivi",
    )
    relying_party = RelyingParty(
        rp_slug=rp_slug,
        organization=organization,
        yivi_tme=yivi_tme,
        ready=False,
        reviewed_accepted=None,
        reviewed_at=None,
        rejection_remarks=None,
        published_at=None,
    )

    relying_party.full_clean()
    relying_party.save()
    return relying_party


def parse_and_validate_hostnames(hostnames: HostnameEntry) -> List[str]:
    new_hostnames = extract_hostnames(hostnames)
    duplicates = [h for h in new_hostnames if hostname_exists(h)]
    if duplicates:
        raise ValidationError(
            {"hostnames": [f"Hostname already exists: {h}" for h in duplicates]}
        )
    return new_hostnames


def create_hostname_objects(
    hostnames: List[str], relying_party: RelyingParty
) -> List[RelyingPartyHostname]:
    created = []
    for hostname in hostnames:
        obj = RelyingPartyHostname(
            relying_party=relying_party,
            hostname=hostname,
            dns_challenge=generate_dns_challenge(),
            dns_challenge_created_at=timezone.now(),
            dns_challenge_verified=False,
        )
        created.append(validate_and_save(obj))
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
            CredentialAttribute,
            name_en=attr["credential_attribute_tag"],
            credential__id=attr["credential_id"],
        )
        cred_id = cred_attr.credential.id
        credential_attributes.setdefault(cred_id, []).append(cred_attr.name_en)

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
    condiscon.full_clean()
    condiscon.save()
    return condiscon


def create_condiscon_attributes(
    condiscon: Condiscon,
    attributes_data: List[AttributeEntry],
) -> None:
    for attr in attributes_data:
        cred_attr = get_object_or_404(
            CredentialAttribute,
            name_en=attr["credential_attribute_tag"],
            credential__id=attr["credential_id"],
        )
        obj = CondisconAttribute(
            credential_attribute=cred_attr,
            condiscon=condiscon,
            reason_en=attr["reason_en"],
            reason_nl=attr["reason_nl"],
        )
        validate_and_save(obj)


def update_relying_party_hostnames(
    relying_party: RelyingParty, submitted_hostnames: List[HostnameEntry]
) -> List[dict[str, str]]:
    rp_existing_hostnames = {
        str(h.id): h
        for h in RelyingPartyHostname.objects.filter(relying_party=relying_party)
    }
    all_hostnames_set = set(
        RelyingPartyHostname.objects.values_list("hostname", flat=True)
    )
    update_or_add = []

    if not submitted_hostnames:
        raise ValidationError("Cannot delete all hostnames.")

    for entry in submitted_hostnames:
        hostname_str = entry.get("hostname", "").strip()
        if not hostname_str:
            continue
        hostname_id = entry.get("id")
        # Update
        if str(hostname_id) in rp_existing_hostnames:
            hostname_obj = rp_existing_hostnames.pop(str(hostname_id))
            if hostname_obj.hostname != hostname_str:
                hostname_obj.hostname = hostname_str
                hostname_obj.dns_challenge = generate_dns_challenge()
                hostname_obj.manually_verified = False
                hostname_obj.dns_challenge_created_at = timezone.now()
                hostname_obj.dns_challenge_verified = False
                validate_and_save(hostname_obj)
            update_or_add.append(hostname_obj)
        # Add new
        elif hostname_str in all_hostnames_set:
            raise ValidationError(
                {"hostnames": [f"Hostname already exists: {hostname_str}"]}
            )
        else:
            new_obj = RelyingPartyHostname(
                relying_party=relying_party,
                hostname=hostname_str,
                dns_challenge=generate_dns_challenge(),
                dns_challenge_created_at=timezone.now(),
                dns_challenge_verified=False,
            )
            update_or_add.append(validate_and_save(new_obj))
            all_hostnames_set.add(hostname_str)
    # Delete old
    for h in rp_existing_hostnames.values():
        h.delete()
    return [
        {"hostname": h.hostname, "dns_challenge": h.dns_challenge}
        for h in update_or_add
    ]


def update_condiscon_attributes(
    condiscon: Condiscon, attributes_data: List[AttributeEntry]
) -> None:
    if condiscon.condiscon is None:
        raise ValidationError("Condiscon JSON is not set.")
    condiscon.condiscon = make_condiscon_json(attributes_data)
    condiscon.full_clean()
    condiscon.save()
    # Delete existing attributes and create new ones
    CondisconAttribute.objects.filter(condiscon=condiscon).delete()
    create_condiscon_attributes(condiscon, attributes_data)


def update_condiscon_context(condiscon: Condiscon, data: RelyingPartyResponse) -> None:
    if "context_description_en" in data:
        condiscon.context_description_en = data["context_description_en"]
    if "context_description_nl" in data:
        condiscon.context_description_nl = data["context_description_nl"]
    condiscon.full_clean()
    condiscon.save()


def update_rp_environment(relying_party: RelyingParty, environment: str) -> None:
    yivi_tme = get_object_or_404(YiviTrustModelEnv, environment=environment)
    relying_party.yivi_tme = yivi_tme
    relying_party.full_clean()
    relying_party.save()


def update_rp_slug(
    relying_party: RelyingParty,
    updated_slug: str,
) -> None | str:
    if updated_slug != relying_party.rp_slug:
        relying_party.rp_slug = updated_slug
        relying_party.full_clean()
        relying_party.save()
        return updated_slug
    return None
