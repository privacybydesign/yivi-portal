from typing import TypedDict


class HostnameEntry(TypedDict):
    id: int
    hostname: str


class AttributeEntry(TypedDict):
    credential_attribute_tag: str
    reason_en: str
    reason_nl: str


class RelyingPartyBaseResponse(TypedDict):
    hostnames: list[HostnameEntry]
    environment: str
    attributes: list[AttributeEntry]
    context_description_en: str
    context_description_nl: str


class RelyingPartyUpdateResponse(RelyingPartyBaseResponse):
    new_rp_slug: str
    ready: bool


class RelyingPartyCreateResponse(RelyingPartyBaseResponse):
    rp_slug: str


RelyingPartyResponse = RelyingPartyCreateResponse | RelyingPartyUpdateResponse


AttributesList = list[str]


class CondisconJSON(TypedDict):
    disclose: list[list[AttributesList]]


CredentialAttributeID = int
CredentialAttributesEntry = dict[CredentialAttributeID, AttributesList]
