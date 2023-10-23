from django.utils import timezone
from dns.resolver import Resolver

from schememanager.models import VerifierHostname


def verify_dns(hostname: VerifierHostname) -> bool:
    """Verify that the DNS challenge is set up correctly"""

    resolver = Resolver()
    answer = resolver.resolve(hostname.hostname, "TXT")

    for item in answer.rrset.items:
        if hostname.dns_challenge == item.to_text():
            hostname.dns_challenge_verified = True
            hostname.dns_challenge_verified_at = timezone.now()
            hostname.save()
            return True

    return False
