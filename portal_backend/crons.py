# from django_cron import CronJobBase, Schedule

# from portal_backend.dns_verification import (
#     verify_new_dns,
#     verify_existing_dns,
# )
# from portal_backend.models.scheme import Scheme
# from portal_backend.models.verifier import VerifierHostname
# from portal_backend.published_check import fetch_requestor_scheme


# class NewDNSVerification(CronJobBase):
#     RUN_EVERY_MINS = 5

#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = "portal_backend.new_dns_verification"

#     def do(self):
#         for hostname in VerifierHostname.objects.filter(dns_challenge_verified=False):
#             verify_new_dns(hostname)


# class ExistingDNSVerification(CronJobBase):
#     RUN_AT_TIMES = ["01:00"]

#     schedule = Schedule(run_at_times=RUN_AT_TIMES)

#     code = "portal_backend.existing_dns_verification"

#     def do(self):
#         for hostname in VerifierHostname.objects.filter(dns_challenge_verified=True):
#             verify_existing_dns(hostname)


# class FetchPublishedSchemes(CronJobBase):
#     RUN_AT_TIMES = ["02:00"]

#     schedule = Schedule(run_at_times=RUN_AT_TIMES)

#     code = "portal_backend.fetch_published_schemes"

#     def do(self):
#         for scheme in Scheme.objects.filter(scheme_type=Scheme.REQUESTOR):
#             fetch_requestor_scheme(scheme)
