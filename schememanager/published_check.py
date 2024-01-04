import logging

import requests
from django.utils import timezone

from schememanager.models.scheme import Scheme
from schememanager.models.verifier import Verifier

logger = logging.getLogger(__name__)


def fetch_requestor_scheme(scheme: Scheme, create_verifiers: bool = False):
    if scheme.scheme_type != Scheme.REQUESTOR:
        raise ValueError("Scheme is not a requestor scheme")

    requestors_url = scheme.url + "/requestors.json"
    requestors_json = requests.get(requestors_url).json()
    if not isinstance(requestors_json, list):
        raise ValueError("Requestors JSON is not a list")

    timestamp_url = scheme.url + "/timestamp"
    timestamp = requests.get(timestamp_url)
    if timestamp.status_code != 200:
        raise ValueError("Timestamp could not be fetched")

    timestamp = timezone.make_aware(
        timezone.datetime.fromtimestamp(int(timestamp.text))
    )

    # TODO check signatures! This requires fetching the whole scheme, not just the requestors.json

    for requestor in requestors_json:
        slug = requestor["id"].split(".")[1]
        if create_verifiers:
            raise NotImplementedError("Creating verifiers is not yet implemented")
            # TODO: this is not implemented yet because it would create orphaned verifiers without an organization
            #  (because we don't have the legal info in the requestor scheme)
        else:
            try:
                verifier = scheme.verifier_set.get(slug=slug)
            except Verifier.DoesNotExist:
                continue

        verifier.published_scheme_data = requestor
        verifier.published_at = timestamp
        logger.info(f"Saving verifier {verifier.slug}")
        verifier.save()
        # TODO save logo's
