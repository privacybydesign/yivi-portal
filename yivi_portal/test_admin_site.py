from unittest.mock import patch

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from yivi_auth.yivi import YiviException
from yivi_portal.admin_site import TOKEN_SESSION_KEY, VERIFIED_SESSION_KEY

EMAIL = "admin@example.com"
# settings/development.py, which the suite runs under, discloses this one.
EMAIL_ATTRIBUTE = "irma-demo.sidn-pbdf.email.email"


def result(email=EMAIL, attribute=EMAIL_ATTRIBUTE, status="DONE", proof="VALID"):
    return {
        "status": status,
        "proofStatus": proof,
        "disclosed": [
            [{"id": attribute, "rawvalue": email, "status": "PRESENT"}],
        ],
    }


class AdminYiviLoginTest(TestCase):
    """The admin opens only after the password *and* a matching Yivi disclosure."""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin", email=EMAIL, password="pw"
        )
        self.index = reverse("admin:index")
        self.verify = reverse("admin:yivi_verify")
        self.start = reverse("admin:yivi_start")
        self.result = reverse("admin:yivi_result")

    def _password_login(self):
        self.client.force_login(self.user)

    def _complete_yivi(self, session_result):
        session = self.client.session
        session[TOKEN_SESSION_KEY] = "requestor-token"
        session.save()
        with patch("yivi_portal.admin_site.YiviServer") as server_cls:
            server_cls.return_value.session_result.return_value = session_result
            return self.client.post(self.result)

    def test_password_alone_does_not_open_the_admin(self):
        self._password_login()
        response = self.client.get(self.index)
        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={self.index}",
            fetch_redirect_response=False,
        )

    def test_login_page_sends_password_verified_staff_to_yivi(self):
        self._password_login()
        response = self.client.get(reverse("admin:login"), {"next": self.index})
        self.assertRedirects(
            response, f"{self.verify}?next=%2Fadmin%2F", fetch_redirect_response=False
        )

    def test_verify_page_renders_the_widget(self):
        self._password_login()
        response = self.client.get(self.verify)
        self.assertContains(response, 'id="yivi-web-form"')
        self.assertContains(response, EMAIL)

    def test_verify_page_requires_the_password_first(self):
        response = self.client.get(self.verify)
        self.assertRedirects(
            response, reverse("admin:login"), fetch_redirect_response=False
        )

    def test_verify_page_ignores_an_offsite_next(self):
        self._password_login()
        response = self.client.get(self.verify, {"next": "https://evil.example/"})
        self.assertNotContains(response, "evil.example")

    def test_start_keeps_the_requestor_token_on_the_server(self):
        self._password_login()
        with patch("yivi_portal.admin_site.YiviServer") as server_cls:
            server_cls.return_value.start_session.return_value = {
                "sessionPtr": {"u": "https://yivi.example/irma/session/x"},
                "token": "requestor-token",
            }
            response = self.client.post(self.start)
            request = server_cls.return_value.start_session.call_args.args[0]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("token", response.json())
        self.assertIn("sessionPtr", response.json())
        self.assertEqual(request["disclose"], [[[EMAIL_ATTRIBUTE]]])
        self.assertEqual(self.client.session[TOKEN_SESSION_KEY], "requestor-token")

    def test_start_requires_the_password_first(self):
        with patch("yivi_portal.admin_site.YiviServer") as server_cls:
            response = self.client.post(self.start)
        self.assertEqual(response.status_code, 403)
        server_cls.return_value.start_session.assert_not_called()

    def test_start_reports_an_unreachable_yivi_server(self):
        self._password_login()
        with patch("yivi_portal.admin_site.YiviServer") as server_cls:
            server_cls.return_value.start_session.side_effect = YiviException(
                500, -1, "down"
            )
            response = self.client.post(self.start)
        self.assertEqual(response.status_code, 502)

    def test_result_reports_an_unreachable_yivi_server(self):
        self._password_login()
        session = self.client.session
        session[TOKEN_SESSION_KEY] = "requestor-token"
        session.save()
        with patch("yivi_portal.admin_site.YiviServer") as server_cls:
            server_cls.return_value.session_result.side_effect = (
                requests.ConnectionError()
            )
            response = self.client.post(self.result)
        self.assertEqual(response.status_code, 502)
        self.assertNotIn(VERIFIED_SESSION_KEY, self.client.session)

    def test_matching_disclosure_opens_the_admin(self):
        self._password_login()
        response = self._complete_yivi(result(email="Admin@Example.com"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(self.index).status_code, 200)

    def test_other_email_is_refused(self):
        self._password_login()
        response = self._complete_yivi(result(email="someone@example.com"))

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(VERIFIED_SESSION_KEY, self.client.session)
        self.assertEqual(self.client.get(self.index).status_code, 302)

    def test_invalid_proof_is_refused(self):
        self._password_login()
        response = self._complete_yivi(result(proof="INVALID"))
        self.assertEqual(response.status_code, 403)

    def test_unfinished_session_is_refused(self):
        self._password_login()
        response = self._complete_yivi(result(status="CANCELLED"))
        self.assertEqual(response.status_code, 403)

    def test_attribute_outside_the_request_is_refused(self):
        self._password_login()
        response = self._complete_yivi(result(attribute="irma-demo.other.email.email"))
        self.assertEqual(response.status_code, 403)

    def test_account_without_email_is_refused(self):
        self.user.email = ""
        self.user.save()
        self._password_login()
        response = self._complete_yivi(result(email=""))
        self.assertEqual(response.status_code, 403)

    def test_result_is_fetched_once(self):
        self._password_login()
        self._complete_yivi(result(email="someone@example.com"))
        with patch("yivi_portal.admin_site.YiviServer") as server_cls:
            response = self.client.post(self.result)
        self.assertEqual(response.status_code, 400)
        server_cls.return_value.session_result.assert_not_called()

    def test_verification_does_not_carry_over_to_another_account(self):
        self._password_login()
        self._complete_yivi(result())

        other = get_user_model().objects.create_superuser(
            username="other", email="other@example.com", password="pw"
        )
        session = self.client.session
        verified = session[VERIFIED_SESSION_KEY]
        self.client.force_login(other)
        session = self.client.session
        session[VERIFIED_SESSION_KEY] = verified
        session.save()

        self.assertEqual(self.client.get(self.index).status_code, 302)
