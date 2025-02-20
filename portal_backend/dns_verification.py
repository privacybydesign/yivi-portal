# import logging

# import dns.resolver
# from django.utils import timezone
# from dns.resolver import Resolver

# from portal_backend.models.verifier import VerifierHostname

# logger = logging.getLogger()


# def verify_dns(hostname: str, challenge: str) -> bool:
#     """Verify that a DNS challenge is set up correctly"""

#     resolver = Resolver()
#     try:
#         answer = resolver.resolve(hostname, "TXT")
#     except dns.resolver.NoAnswer:
#         return False
#     except dns.resolver.NXDOMAIN:
#         return False

#     return any(challenge == item.to_text() for item in answer.rrset.items)


# def verify_new_dns(hostname: VerifierHostname) -> bool:
#     """Verify that a new DNS challenge is set up correctly"""

#     if hostname.dns_challenge_verified:
#         raise ValueError("Expecting a new hostname")

#     verified = verify_dns(hostname.hostname, hostname.dns_challenge)

#     if verified:
#         hostname.dns_challenge_verified = True
#         hostname.dns_challenge_verified_at = timezone.now()
#         hostname.dns_challenge_invalidated_at = None
#         hostname.save()
#         logger.info(f"DNS challenge for {hostname.hostname} verified")
#         return True

#     return False


# def verify_existing_dns(hostname: VerifierHostname) -> bool:
#     """Verify that the DNS challenge is still set up correctly"""

#     if not hostname.dns_challenge_verified:
#         raise ValueError("Expecting an already verified hostname")

#     verified = verify_dns(hostname.hostname, hostname.dns_challenge)

#     if not verified:
#         hostname.dns_challenge_verified = False
#         hostname.dns_challenge_invalidated_at = timezone.now()
#         hostname.save()
#         logger.info(f"DNS challenge for {hostname.hostname} invalidated")
#         return False

#     return True
