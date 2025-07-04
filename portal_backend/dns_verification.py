import logging
import secrets
import dns.resolver  # type: ignore
from django.utils import timezone
from dns.resolver import Resolver  # type: ignore
from portal_backend.models.models import RelyingPartyHostname

logger = logging.getLogger(__name__)


def verify_dns(hostname: str, challenge: str) -> bool:
    """Verify that a DNS challenge is set up correctly"""
    resolver = Resolver()
    try:
        answer = resolver.resolve(hostname, "TXT")
    except dns.resolver.NoAnswer:
        logger.warning(f"No TXT record found for {hostname}")
        return False
    except dns.resolver.NXDOMAIN:
        logger.warning(f"Domain {hostname} does not exist")
        return False
    except dns.resolver.LifetimeTimeout:
        logger.error(f"DNS resolution timed out for {hostname}")
        return False

    return any(challenge == item.to_text() for item in answer.rrset.items)


def verify_new_dns(hostname: RelyingPartyHostname) -> bool:
    """Verify that a new DNS challenge is set up correctly"""
    if hostname.dns_challenge_verified:
        raise ValueError("Expecting a new hostname")

    verified = verify_dns(hostname.hostname, hostname.dns_challenge)

    if verified:
        hostname.dns_challenge_verified = True
        hostname.dns_challenge_verified_at = timezone.now()
        hostname.dns_challenge_invalidated_at = None
        hostname.save()
        logger.info(f"DNS challenge for {hostname.hostname} verified")
        return True

    logger.warning(f"DNS challenge for {hostname.hostname} failed to verify")


def verify_existing_dns(hostname: RelyingPartyHostname) -> bool:
    """Verify that the DNS challenge is still set up correctly"""
    if not hostname.dns_challenge_verified:
        raise ValueError("Expecting an already verified hostname")

    verified = verify_dns(hostname.hostname, hostname.dns_challenge)

    if not verified:
        hostname.dns_challenge_verified = False
        hostname.dns_challenge_invalidated_at = timezone.now()
        hostname.save()
        logger.info(f"DNS challenge for {hostname.hostname} invalidated")
        return False

    return True


def generate_dns_challenge() -> str:
    """Generate a new DNS challenge token"""
    random = secrets.token_hex(16)
    return f'"yivi_verifier_challenge={random}"'
