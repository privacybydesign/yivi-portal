from unittest.mock import call, patch

from django.test import TestCase, override_settings
from django.urls import reverse

SPLIT_SERVER_SETTINGS = {
    "YIVI_SERVER_URL": "https://auth.example",
    "YIVI_SERVER_TOKEN": "auth-token",
    "YIVI_ISSUANCE_SERVER_URL": "https://issuance.example",
    "YIVI_ISSUANCE_SERVER_TOKEN": "issuance-token",
}


class YiviIssueDemosViewTest(TestCase):
    """Tests for the demo-credential issuance proxy view.

    The per-attribute value fields are optional: empty fields must be omitted
    from the issuance request so a demo credential can be issued without filling
    in every attribute.
    """

    def setUp(self):
        self.url = reverse("yivi_auth:demo_issuance")

    def _post(self, payload):
        """POST to the demo-issuance endpoint with YiviServer mocked.

        Returns the session_request that was forwarded to the Yivi server.
        """
        with patch("yivi_auth.views.YiviServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.start_session.return_value = {
                "sessionPtr": {"u": "http://example", "irmaqr": "issuing"},
                "token": "abc123",
            }
            response = self.client.post(
                self.url, data=payload, content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(mock_server.start_session.called)
            session_request = mock_server.start_session.call_args.args[0]
            self.server_args = mock_server_cls.call_args
        return session_request

    def test_empty_attributes_are_omitted_from_issuance(self):
        """Attributes left empty should not be forwarded to the Yivi server."""
        session_request = self._post(
            {
                "credential": "irma-demo.test-org.demo",
                "attributes": {
                    "filled": "value",
                    "blank": "",
                    "whitespace": "   ",
                    "another_filled": "second",
                },
            }
        )

        forwarded = session_request["credentials"][0]["attributes"]
        self.assertEqual(
            forwarded, {"filled": "value", "another_filled": "second"}
        )
        # Empty / whitespace-only fields are dropped entirely.
        self.assertNotIn("blank", forwarded)
        self.assertNotIn("whitespace", forwarded)

    def test_all_attributes_filled_are_all_forwarded(self):
        """When every field is filled, all attributes are forwarded unchanged."""
        session_request = self._post(
            {
                "credential": "irma-demo.test-org.demo",
                "attributes": {"a": "1", "b": "2"},
            }
        )

        forwarded = session_request["credentials"][0]["attributes"]
        self.assertEqual(forwarded, {"a": "1", "b": "2"})

    def test_missing_attributes_key_is_handled(self):
        """A request without an attributes key issues with no attributes."""
        session_request = self._post({"credential": "irma-demo.test-org.demo"})

        forwarded = session_request["credentials"][0]["attributes"]
        self.assertEqual(forwarded, {})

    @override_settings(YIVI_SDJWT_BATCH_SIZE=7)
    def test_sdjwt_batch_size_from_settings_is_forwarded(self):
        """The issuance request asks for SD-JWT VCs in the configured batch size."""
        session_request = self._post({"credential": "irma-demo.test-org.demo"})

        self.assertEqual(session_request["credentials"][0]["sdJwtBatchSize"], 7)

    @override_settings(**SPLIT_SERVER_SETTINGS)
    def test_demo_issuance_targets_the_issuance_server(self):
        """Demo issuance uses the dedicated issuance server, not the auth one."""
        self._post({"credential": "irma-demo.test-org.demo"})

        self.assertEqual(
            self.server_args, call("https://issuance.example", token="issuance-token")
        )


class YiviDemoIssuanceResultViewTest(TestCase):
    @override_settings(**SPLIT_SERVER_SETTINGS)
    def test_result_targets_the_issuance_server(self):
        """The session result must be fetched from the server that started it."""
        url = reverse("yivi_auth:demo_issuance_token", kwargs={"yivi_token": "abc123"})
        with patch("yivi_auth.views.YiviServer") as mock_server_cls:
            mock_server_cls.return_value.session_result.return_value = {
                "status": "DONE"
            }
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            mock_server_cls.call_args,
            call("https://issuance.example", token="issuance-token"),
        )


class YiviSessionProxyStartViewTest(TestCase):
    @override_settings(**SPLIT_SERVER_SETTINGS)
    def test_login_targets_the_general_server(self):
        """Authentication keeps using the general Yivi server."""
        with patch("yivi_auth.views.YiviServer") as mock_server_cls:
            mock_server_cls.return_value.start_session.return_value = {
                "sessionPtr": {"u": "http://example", "irmaqr": "disclosing"},
                "token": "abc123",
            }
            response = self.client.post(
                reverse("yivi_auth:start"), data={}, content_type="application/json"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            mock_server_cls.call_args, call("https://auth.example", token="auth-token")
        )
