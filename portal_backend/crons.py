from portal_backend.dns_verification import verify_new_dns, verify_existing_dns
from portal_backend.models.models import RelyingPartyHostname
from portal_backend.scheme_utils.check_published import check_published_cron
from portal_backend.scheme_utils.trusted_aps_import import import_aps
from portal_backend.scheme_utils.trusted_rps_import import import_rps


class NewDNSVerification:
    def do(self):
        for hostname in RelyingPartyHostname.objects.filter(
            dns_challenge_verified=False
        ):
            verify_new_dns(hostname)


class ExistingDNSVerification:
    def do(self):
        for hostname in RelyingPartyHostname.objects.filter(
            dns_challenge_verified=True
        ):
            verify_existing_dns(hostname)


class TrustedAPsImport:
    def do(self):
        import_aps()


class TrustedRPsImport:
    def do(self):
        import_rps()


class CheckPublishedRelyingParties:
    def do(self):
        check_published_cron()
