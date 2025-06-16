from typing import TypedDict, List, Union


class HostnameEntry(TypedDict):
    id: int
    hostname: str


class AttributeEntry(TypedDict):
    credential_attribute_id: str
    reason_en: str
    reason_nl: str


class RelyingPartyBaseResponse(TypedDict):
    hostnames: List[HostnameEntry]
    environment: str
    attributes: List[AttributeEntry]
    context_description_en: str
    context_description_nl: str


class RelyingPartyUpdateResponse(RelyingPartyBaseResponse):
    new_rp_slug: str
    ready: bool


class RelyingPartyCreateResponse(RelyingPartyBaseResponse):
    rp_slug: str


RelyingPartyResponse = Union[RelyingPartyCreateResponse, RelyingPartyUpdateResponse]


AttributesList = List[str]


class CondisconJSON(TypedDict):
    disclose: List[List[AttributesList]]


CredentialAttributeID = int
CredentialAttributesEntry = dict[CredentialAttributeID, AttributesList]
