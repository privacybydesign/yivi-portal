import base64
import json
from datetime import UTC, datetime

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken  # type: ignore

from portal_backend.models.models import Organization, UsageReport, UsageServerKey
from portal_backend.models.models import User as OrgUser
from portal_backend.services import usage

PROBLEM = "urn:ietf:params:acme:error:"


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def public_pem(key: ec.EllipticCurvePrivateKey) -> str:
    return (
        key.public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )


def make_report(report_id="r1", sequence=1, final=False, run_id="run-1"):
    return {
        "schema": 1,
        "report_id": report_id,
        "server_instance": "irma-prod-1",
        "run_id": run_id,
        "sequence": sequence,
        "final": final,
        "irmago_version": "1.5.0",
        "period": {"from": "2026-10-29T14:05:00Z", "to": "2026-10-29T14:10:00Z"},
        "disclosures": [
            {
                "day": "2026-10-29",
                "requestor": "webshop",
                "action": "disclosing",
                "credential_type": "pbdf.gemeente.personalData",
                "outcome": "done",
                "count": 12,
            },
            {
                "day": "2026-10-29",
                "requestor": "webshop",
                "action": "disclosing",
                "credential_type": "pbdf.gemeente.personalData",
                "outcome": "timeout",
                "count": 1,
            },
        ],
        "sessions": [
            {
                "day": "2026-10-29",
                "requestor": "webshop",
                "action": "disclosing",
                "outcome": "done",
                "count": 12,
            },
        ],
    }


class UsageServer:
    """Talks to the usage API the way a Yivi server does."""

    def __init__(self, test: TestCase, key=None):
        self.test = test
        self.key = key or ec.generate_private_key(ec.SECP256R1())
        self.kid = None

    def nonce(self) -> str:
        response = self.test.client.head(reverse("portal_backend:usage-new-nonce"))
        self.test.assertEqual(response.status_code, 200)
        return response["Replay-Nonce"]

    def jws(self, url: str, payload: dict, nonce=None, kid=None, key=None) -> str:
        key = key or self.key
        protected = {"alg": "ES256", "nonce": nonce or self.nonce(), "url": url}
        if kid:
            protected["kid"] = kid
        else:
            protected["jwk"] = usage.jwk_from_public_key(key.public_key())
        signing_input = (
            f"{b64(json.dumps(protected).encode())}.{b64(json.dumps(payload).encode())}"
        )
        r, s = decode_dss_signature(
            key.sign(signing_input.encode(), ec.ECDSA(hashes.SHA256()))
        )
        protected_b64, payload_b64 = signing_input.split(".")
        return json.dumps(
            {
                "protected": protected_b64,
                "payload": payload_b64,
                "signature": b64(r.to_bytes(32, "big") + s.to_bytes(32, "big")),
            }
        )

    def post(self, path: str, body: str):
        return self.test.client.post(path, body, content_type="application/jose+json")

    def lookup_account(self):
        path = reverse("portal_backend:usage-new-account")
        response = self.post(
            path, self.jws(f"http://testserver{path}", {"onlyReturnExisting": True})
        )
        if response.status_code == 200:
            self.kid = response["Location"]
        return response

    def send_report(self, report: dict, **kwargs):
        path = self.kid.removeprefix("http://testserver") + "/reports"
        return self.post(
            path, self.jws(f"http://testserver{path}", report, kid=self.kid, **kwargs)
        )


class UsageApiTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name_en="Webshop", name_nl="Webwinkel", slug="webshop"
        )
        self.server = UsageServer(self)

    def register(self, server=None):
        return usage.register_key(
            self.organization, public_pem((server or self.server).key), "test"
        )

    def test_directory(self):
        response = self.client.get(reverse("portal_backend:usage-directory"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "newNonce": "http://testserver/usage/v1/new-nonce",
                "newAccount": "http://testserver/usage/v1/new-account",
            },
        )

    def test_unregistered_key_has_no_account(self):
        response = self.server.lookup_account()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["type"], PROBLEM + "accountDoesNotExist")
        self.assertIn("Replay-Nonce", response)

    def test_report_is_stored_once(self):
        server_key = self.register()
        self.assertEqual(self.server.lookup_account().status_code, 200)
        self.assertTrue(self.server.kid.endswith(f"/usage/v1/accounts/{server_key.id}"))

        response = self.server.send_report(make_report())
        self.assertEqual(response.status_code, 201)
        report = UsageReport.objects.get()
        self.assertEqual(report.server_key, server_key)
        self.assertEqual(report.sequence, 1)
        self.assertEqual(report.disclosures.count(), 2)
        self.assertEqual(report.sessions.get().count, 12)

        # A retry after a lost response is answered 200 and stored nothing new.
        response = self.server.send_report(make_report())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UsageReport.objects.count(), 1)

    def test_nonce_is_single_use(self):
        self.register()
        self.server.lookup_account()
        nonce = self.server.nonce()
        self.assertEqual(
            self.server.send_report(make_report(), nonce=nonce).status_code, 201
        )
        response = self.server.send_report(make_report("r2", 2), nonce=nonce)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["type"], PROBLEM + "badNonce")

    def test_report_signed_by_other_key_is_refused(self):
        self.register()
        self.server.lookup_account()
        other = ec.generate_private_key(ec.SECP256R1())
        response = self.server.send_report(make_report(), key=other)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(UsageReport.objects.exists())

    def test_jws_for_other_url_is_refused(self):
        self.register()
        self.server.lookup_account()
        path = self.server.kid.removeprefix("http://testserver") + "/reports"
        body = self.server.jws(
            "http://testserver/usage/v1/new-account", make_report(), kid=self.server.kid
        )
        self.assertEqual(self.server.post(path, body).status_code, 401)

    def test_deactivated_key_is_refused(self):
        server_key = self.register()
        self.server.lookup_account()
        server_key.deactivated_at = datetime.now(UTC)
        server_key.save()

        response = self.server.send_report(make_report())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.server.lookup_account().status_code, 400)

    def test_malformed_report_is_refused(self):
        self.register()
        self.server.lookup_account()
        report = make_report()
        report["disclosures"][0]["outcome"] = "unknown"
        response = self.server.send_report(report)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["type"], PROBLEM + "malformed")
        self.assertFalse(UsageReport.objects.exists())

    def test_thumbprint_matches_rfc7638(self):
        # RFC 7638 section 3.1 example key, which is RSA; the EC computation follows the same
        # rule: the required members, lexicographic order, no whitespace.
        key = ec.generate_private_key(ec.SECP256R1())
        jwk = usage.jwk_from_public_key(key.public_key())
        canonical = f'{{"crv":"P-256","kty":"EC","x":"{jwk["x"]}","y":"{jwk["y"]}"}}'
        import hashlib

        self.assertEqual(
            usage.thumbprint(key.public_key()),
            b64(hashlib.sha256(canonical.encode()).digest()),
        )


class UsageMaintainerApiTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name_en="Webshop", name_nl="Webwinkel", slug="webshop"
        )
        self.other_organization = Organization.objects.create(
            name_en="Other", name_nl="Ander", slug="other"
        )
        user = get_user_model().objects.create_user(
            email="maintainer@webshop.nl", username="maintainer@webshop.nl"
        )
        org_user = OrgUser.objects.create(email=user.email, role="maintainer")
        org_user.organizations.add(self.organization)
        token = AccessToken.for_user(user)
        token["organizationSlugs"] = [self.organization.slug]
        self.api = APIClient()
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {token!s}")
        self.server = UsageServer(self)

    def test_register_list_and_deactivate_key(self):
        url = reverse("portal_backend:usage-keys", args=["webshop"])
        # The whole output of `irma server usage-key` may be pasted.
        pasted = public_pem(self.server.key) + "JWK thumbprint: abc\n"
        response = self.api.post(
            url, {"public_key_pem": pasted, "label": "prod"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["thumbprint"], usage.thumbprint(self.server.key.public_key())
        )

        response = self.api.post(url, {"public_key_pem": pasted}, format="json")
        self.assertEqual(response.status_code, 409)

        response = self.api.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]["is_active"])

        key_id = response.data[0]["id"]
        response = self.api.delete(
            reverse("portal_backend:usage-key", args=["webshop", key_id])
        )
        self.assertEqual(response.status_code, 204)
        self.assertIsNotNone(UsageServerKey.objects.get().deactivated_at)

    def test_rejects_non_p256_key(self):
        rsa_like = ec.generate_private_key(ec.SECP384R1())
        response = self.api.post(
            reverse("portal_backend:usage-keys", args=["webshop"]),
            {"public_key_pem": public_pem(rsa_like)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_other_organization_is_forbidden(self):
        response = self.api.get(reverse("portal_backend:usage-keys", args=["other"]))
        self.assertEqual(response.status_code, 403)
        response = self.api.get(reverse("portal_backend:usage-summary", args=["other"]))
        self.assertEqual(response.status_code, 403)

    def test_summary_sums_reports_and_lists_gaps(self):
        usage.register_key(self.organization, public_pem(self.server.key))
        self.server.lookup_account()
        self.server.send_report(make_report("r1", 1))
        self.server.send_report(make_report("r3", 3))  # report 2 never arrived

        response = self.api.get(
            reverse("portal_backend:usage-summary", args=["webshop"])
        )
        self.assertEqual(response.status_code, 200)
        done = [d for d in response.data["disclosures"] if d["outcome"] == "done"]
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0]["count"], 24)
        self.assertEqual(done[0]["credential_type"], "pbdf.gemeente.personalData")
        self.assertEqual(response.data["sessions"][0]["count"], 24)
        self.assertEqual(len(response.data["gaps"]), 1)
        self.assertEqual(response.data["gaps"][0]["missing_sequences"], [2])
        self.assertFalse(response.data["gaps"][0]["final"])

        response = self.api.get(
            reverse("portal_backend:usage-summary", args=["webshop"]),
            {"from": "2026-10-30"},
        )
        self.assertEqual(response.data["disclosures"], [])

    def test_complete_run_has_no_gap(self):
        usage.register_key(self.organization, public_pem(self.server.key))
        self.server.lookup_account()
        self.server.send_report(make_report("r1", 1))
        self.server.send_report(make_report("r2", 2, final=True))
        response = self.api.get(
            reverse("portal_backend:usage-summary", args=["webshop"])
        )
        self.assertEqual(response.data["gaps"], [])


class RegisterUsageKeyCommandTest(TestCase):
    def test_registers_key(self):
        Organization.objects.create(
            name_en="Webshop", name_nl="Webwinkel", slug="webshop"
        )
        key = ec.generate_private_key(ec.SECP256R1())
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as f:
            f.write(public_pem(key))
        call_command("register_usage_key", "webshop", f.name, label="e2e")
        self.assertEqual(
            UsageServerKey.objects.get().thumbprint, usage.thumbprint(key.public_key())
        )
