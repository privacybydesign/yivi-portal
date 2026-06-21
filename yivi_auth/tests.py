from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


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
