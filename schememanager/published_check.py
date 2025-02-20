# import logging
# import os

# import requests
# from django.conf import settings
# from django.utils import timezone

# from schememanager.models.scheme import Scheme
# from schememanager.models.verifier import Verifier

# logger = logging.getLogger()


# def fetch_requestor_scheme(scheme: Scheme, create_verifiers: bool = False):
#     if scheme.scheme_type != Scheme.REQUESTOR:
#         raise ValueError("Scheme is not a requestor scheme")

#     requestors_url = scheme.url + "/requestors.json"
#     requestors_json = requests.get(requestors_url).json()
#     if not isinstance(requestors_json, list):
#         raise ValueError("Requestors JSON is not a list")

#     timestamp_url = scheme.url + "/timestamp"
#     timestamp = requests.get(timestamp_url)
#     if timestamp.status_code != 200:
#         raise ValueError("Timestamp could not be fetched")

#     timestamp = timezone.make_aware(
#         timezone.datetime.fromtimestamp(int(timestamp.text))
#     )

#     # TODO check signatures! This requires fetching the whole scheme, not just the requestors.json

#     for requestor in requestors_json:
#         slug = requestor["id"].split(".")[1]
#         try:
#             verifier = scheme.verifier_set.get(slug=slug)
#         except Verifier.DoesNotExist:
#             if not create_verifiers:
#                 continue

#             verifier = Verifier.objects.create(
#                 scheme=scheme,
#                 slug=slug,
#                 name_en=requestor["name"]["en"],
#                 name_nl=requestor["name"]["nl"],
#                 published_scheme_data=requestor,
#                 published_at=timestamp,
#                 ready=True,
#             )

#             if "logo" in requestor:
#                 filename = requestor["logo"] + ".png"
#                 logo_url = scheme.url + "/assets/" + filename
#                 logo = requests.get(logo_url)

#                 if logo.status_code == 200:
#                     filepath = os.path.join(settings.MEDIA_ROOT, filename)
#                     with open(filepath, "wb") as f:
#                         for chunk in logo.iter_content(1024):
#                             f.write(chunk)
#                     verifier.logo = filename
#                     verifier.approved_logo = filename
#                     verifier.save()
#                 else:
#                     logger.warning(f"Could not fetch logo for {verifier.slug}")

#             for host in requestor["hostnames"]:
#                 verifier.hostnames.create(hostname=host, manually_verified=True)

#         verifier.published_scheme_data = requestor
#         verifier.published_at = timestamp
#         logger.info(f"Saving verifier {verifier.slug}")
#         verifier.save()
#         # TODO save logo's
