"""Monthly usage per requestor and credential type, its CSV export, and the gaps in a month."""

import csv
import io
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import ec
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken  # type: ignore

from portal_backend.models.models import Organization, UsageReport, UsageServerKey
from portal_backend.models.models import User as OrgUser
from portal_backend.services import usage
from portal_backend.tests.test_usage import public_pem

OCT_1 = datetime(2026, 10, 1, tzinfo=UTC)
NOV_1 = datetime(2026, 11, 1, tzinfo=UTC)
HOUR = timedelta(hours=1)


def at(day: int, hour: int = 0) -> datetime:
    return datetime(2026, 10, day, hour, tzinfo=UTC)


def iso(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


def report(
    sequence: int,
    period_from: datetime,
    period_to: datetime,
    run_id="run-1",
    final=False,
    heartbeat: int | None = 3600,
    server_instance="irma-prod-1",
    sessions=(),
    credentials=(),
) -> dict:
    payload = {
        "schema": 1,
        "report_id": f"{server_instance}-{run_id}-{sequence}",
        "server_instance": server_instance,
        "run_id": run_id,
        "sequence": sequence,
        "final": final,
        "irmago_version": "1.6.0" if heartbeat else "1.5.0",
        "period": {"from": iso(period_from), "to": iso(period_to)},
        "sessions": [
            {
                "day": day,
                "requestor": requestor,
                "action": action,
                "outcome": outcome,
                "count": count,
            }
            for day, requestor, action, outcome, count in sessions
        ],
        "disclosures": [
            {
                "day": day,
                "requestor": requestor,
                "action": action,
                "credential_type": credential_type,
                "outcome": outcome,
                "count": count,
            }
            for day, requestor, action, credential_type, outcome, count in credentials
        ],
    }
    if heartbeat:
        payload["heartbeat_seconds"] = heartbeat
    return payload


def hourly_run(
    first: datetime, last: datetime, run_id="run-1", final=False, skip=(), **kwargs
):
    """Reports every hour from first to last, like a quiet server with a heartbeat."""
    reports, sequence, moment = [], 0, first
    while moment < last:
        sequence += 1
        end = min(moment + HOUR, last)
        if sequence not in skip:
            reports.append(
                report(
                    sequence,
                    moment,
                    end,
                    run_id=run_id,
                    final=final and end == last,
                    **kwargs,
                )
            )
        moment = end
    return reports


class MonthlyUsageTestCase(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name_en="Webshop", name_nl="Webwinkel", slug="webshop", is_verified=True
        )
        self.key = usage.register_key(
            self.organization, public_pem(ec.generate_private_key(ec.SECP256R1()))
        )
        # Registered long before the month, unless a test says otherwise.
        UsageServerKey.objects.filter(pk=self.key.pk).update(
            created_at=OCT_1 - timedelta(days=60)
        )
        self.key.refresh_from_db()

    def store(self, *reports):
        for payload in reports:
            usage.store_report(self.key, payload)

    def completeness(self, now=NOV_1 + timedelta(days=5)):
        return usage.month_completeness(self.organization, 2026, 10, now=now)

    def gaps(self, **kwargs):
        return [
            (gap["kind"], gap["from"], gap["to"])
            for gap in self.completeness(**kwargs)["gaps"]
        ]


class MonthlyUsageTest(MonthlyUsageTestCase):
    def setUp(self):
        super().setUp()
        # One session at the webshop disclosed three credential types; another only email.
        self.store(
            report(
                1,
                at(29),
                at(29, 1),
                sessions=[
                    ("2026-10-29", "webshop", "disclosing", "done", 2),
                    ("2026-10-29", "webshop", "disclosing", "timeout", 1),
                    ("2026-10-29", "bank", "signing", "done", 1),
                    ("2026-10-29", "webshop", "issuing", "done", 4),
                    ("2026-09-30", "webshop", "disclosing", "done", 7),
                ],
                credentials=[
                    (
                        "2026-10-29",
                        "webshop",
                        "disclosing",
                        "pbdf.sidn-pbdf.email",
                        "done",
                        2,
                    ),
                    (
                        "2026-10-29",
                        "webshop",
                        "disclosing",
                        "pbdf.pbdf.idin",
                        "done",
                        1,
                    ),
                    (
                        "2026-10-29",
                        "webshop",
                        "disclosing",
                        "pbdf.gemeente.personalData",
                        "done",
                        1,
                    ),
                    (
                        "2026-10-29",
                        "webshop",
                        "disclosing",
                        "pbdf.pbdf.idin",
                        "timeout",
                        1,
                    ),
                    ("2026-10-29", "bank", "signing", "pbdf.pbdf.idin", "done", 1),
                ],
            ),
            # A second report adds to the first instead of replacing it.
            report(
                2,
                at(29, 1),
                at(29, 2),
                sessions=[("2026-10-29", "webshop", "disclosing", "done", 1)],
                credentials=[
                    ("2026-10-29", "webshop", "disclosing", "pbdf.pbdf.idin", "done", 1)
                ],
            ),
        )

    def test_counts_billed_sessions_and_credentials_separately(self):
        data = usage.monthly_usage(self.organization, 2026, 10)
        self.assertEqual(data["month"], "2026-10")
        self.assertEqual(data["actions"], ["disclosing", "signing"])
        self.assertEqual(data["outcomes"], ["done"])
        self.assertEqual(
            [(r["requestor"], r["action"], r["count"]) for r in data["sessions"]],
            [("bank", "signing", 1), ("webshop", "disclosing", 3)],
        )
        self.assertEqual(
            [
                (r["requestor"], r["credential_type"], r["count"])
                for r in data["credentials"]
            ],
            [
                ("bank", "pbdf.pbdf.idin", 1),
                ("webshop", "pbdf.gemeente.personalData", 1),
                ("webshop", "pbdf.pbdf.idin", 2),
                ("webshop", "pbdf.sidn-pbdf.email", 2),
            ],
        )

    def test_other_actions_and_outcomes_on_request(self):
        data = usage.monthly_usage(
            self.organization, 2026, 10, ["disclosing", "issuing"], ["timeout"]
        )
        self.assertEqual(
            [(r["action"], r["outcome"], r["count"]) for r in data["sessions"]],
            [("disclosing", "timeout", 1)],
        )


class MonthlyUsageApiTest(MonthlyUsageTestCase):
    def setUp(self):
        super().setUp()
        Organization.objects.create(name_en="Other", name_nl="Ander", slug="other")
        user = get_user_model().objects.create_user(
            email="maintainer@webshop.nl", username="maintainer@webshop.nl"
        )
        org_user = OrgUser.objects.create(email=user.email, role="maintainer")
        org_user.organizations.add(self.organization)
        token = AccessToken.for_user(user)
        token["organizationSlugs"] = [self.organization.slug]
        self.api = APIClient()
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {token!s}")
        self.store(
            report(
                1,
                at(29),
                at(29, 1),
                sessions=[
                    ("2026-10-29", "=HYPERLINK(1)", "disclosing", "done", 2),
                    ("2026-10-29", "webshop", "disclosing", "cancelled", 1),
                ],
                credentials=[
                    (
                        "2026-10-29",
                        "=HYPERLINK(1)",
                        "disclosing",
                        "pbdf.pbdf.idin",
                        "done",
                        2,
                    )
                ],
            )
        )

    def url(self, slug="webshop", csv_export=False):
        name = "usage-monthly-csv" if csv_export else "usage-monthly"
        return reverse(f"portal_backend:{name}", args=[slug])

    def test_month_as_json(self):
        response = self.api.get(self.url(), {"month": "2026-10"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["sessions"][0]["count"], 2)
        self.assertEqual(len(response.data["sessions"]), 1)
        self.assertFalse(response.data["completeness"]["complete"])

        response = self.api.get(
            self.url(), {"month": "2026-10", "outcome": ["cancelled", "done"]}
        )
        self.assertEqual(response.data["outcomes"], ["done", "cancelled"])
        self.assertEqual(len(response.data["sessions"]), 2)

    def test_invalid_query_is_refused(self):
        for query in (
            {},
            {"month": "2026-13"},
            {"month": "2026-1"},
            {"month": "0000-10"},
            {"month": "9999-12"},
            {"month": "²⁰²⁶-10"},
            {"month": "2026-10", "action": "deleting"},
            {"month": "2026-10", "outcome": "maybe"},
        ):
            with self.subTest(query=query):
                response = self.api.get(self.url(), query)
                self.assertEqual(response.status_code, 400)

    def test_other_organization_is_forbidden(self):
        for csv_export in (False, True):
            response = self.api.get(self.url("other", csv_export), {"month": "2026-10"})
            self.assertEqual(response.status_code, 403)

    def test_month_as_csv(self):
        response = self.api.get(self.url(csv_export=True), {"month": "2026-10"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("yivi-usage-webshop-2026-10.csv", response["Content-Disposition"])
        # A byte order mark makes spreadsheet programs read the file as UTF-8.
        self.assertTrue(response.content.startswith("\ufeff".encode()))
        rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8-sig"))))
        sessions = [r for r in rows if r["metric"] == "sessions"]
        credentials = [r for r in rows if r["metric"] == "credentials"]
        gaps = [r for r in rows if r["metric"].startswith("gap:")]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["count"], "2")
        # A requestor name that a spreadsheet would run as a formula is neutralised.
        self.assertEqual(sessions[0]["requestor"], "'=HYPERLINK(1)")
        self.assertEqual(credentials[0]["credential_type"], "pbdf.pbdf.idin")
        self.assertTrue(gaps)
        self.assertTrue(all(r["complete"] == "false" for r in rows))


class ReportHeartbeatTest(MonthlyUsageTestCase):
    def test_heartbeat_is_stored(self):
        self.store(report(1, at(1), at(1, 1), heartbeat=3600))
        self.store(report(2, at(1, 1), at(1, 2), heartbeat=None))
        self.assertEqual(
            list(
                UsageReport.objects.order_by("sequence").values_list(
                    "heartbeat_seconds", flat=True
                )
            ),
            [3600, None],
        )

    def test_invalid_heartbeat_is_malformed(self):
        for heartbeat in (0, -1, "3600", True, 10**9):
            with self.subTest(heartbeat=heartbeat):
                payload = report(1, at(1), at(1, 1))
                payload["heartbeat_seconds"] = heartbeat
                with self.assertRaises(usage.UsageProblem):
                    usage.store_report(self.key, payload)


class MonthCompletenessTest(MonthlyUsageTestCase):
    def test_month_covered_by_heartbeats_is_complete(self):
        self.store(*hourly_run(OCT_1 - HOUR, NOV_1 + HOUR))
        result = self.completeness()
        self.assertEqual(result["gaps"], [])
        self.assertTrue(result["complete"])
        self.assertEqual(result["reported_until"], NOV_1 + HOUR)

    def test_cleanly_stopped_server_has_no_gap(self):
        # Stopped on the 10th, started again on the 20th: no sessions in between.
        self.store(*hourly_run(OCT_1, at(10), final=True))
        self.store(*hourly_run(at(20), NOV_1 + HOUR, run_id="run-2"))
        self.assertEqual(self.gaps(), [])

    def test_missing_report_is_a_gap(self):
        self.store(*hourly_run(OCT_1, NOV_1 + HOUR, skip={5, 6}))
        result = self.completeness()
        self.assertFalse(result["complete"])
        [gap] = result["gaps"]
        self.assertEqual(
            (gap["kind"], gap["from"], gap["to"]),
            ("missing_reports", at(1, 4), at(1, 6)),
        )
        self.assertEqual(gap["missing_count"], 2)
        self.assertEqual(gap["server_instance"], "irma-prod-1")

    def test_crashed_run_is_a_gap_until_the_next_run(self):
        self.store(*hourly_run(OCT_1, at(10)))
        self.store(*hourly_run(at(10, 3), NOV_1 + HOUR, run_id="run-2"))
        self.assertEqual(self.gaps(), [("interrupted", at(10), at(10, 3))])

    def test_silent_server_is_a_gap(self):
        self.store(*hourly_run(OCT_1, at(10)))
        self.assertEqual(self.gaps(), [("interrupted", at(10), NOV_1)])

    def test_current_month_only_counts_until_now(self):
        self.store(*hourly_run(OCT_1, at(10)))
        # Within the heartbeat and its grace, silence is not yet a gap.
        self.assertEqual(self.gaps(now=at(10, 1)), [])
        self.assertEqual(self.gaps(now=at(12)), [("interrupted", at(10), at(12))])

    def test_server_without_heartbeat_cannot_be_judged(self):
        self.store(
            report(1, at(3), at(3, 1), heartbeat=None),
            report(2, at(9), at(9, 1), heartbeat=None),
        )
        [gap] = self.completeness()["gaps"]
        self.assertEqual(
            (gap["kind"], gap["from"], gap["to"]), ("no_heartbeat", at(3), NOV_1)
        )
        self.assertEqual(gap["irmago_version"], "1.5.0")

    def test_run_that_went_silent_before_the_month_is_a_gap(self):
        self.store(*hourly_run(OCT_1 - timedelta(days=3), OCT_1 - timedelta(days=2)))
        self.assertEqual(self.gaps(), [("interrupted", OCT_1, NOV_1)])

    def test_no_reports_at_all(self):
        self.assertEqual(self.gaps(), [("no_reports", OCT_1, NOV_1)])

    def test_period_without_an_active_key(self):
        UsageServerKey.objects.filter(pk=self.key.pk).update(
            created_at=at(10), deactivated_at=at(20)
        )
        self.assertEqual(
            self.gaps(),
            [
                ("no_key", OCT_1, at(10)),
                ("no_reports", at(10), at(20)),
                ("no_key", at(20), NOV_1),
            ],
        )

    def test_reports_from_before_the_key_was_registered_count(self):
        # The server keeps its reports until its key is registered, and sends them then.
        UsageServerKey.objects.filter(pk=self.key.pk).update(created_at=at(15))
        self.store(*hourly_run(OCT_1 - HOUR, NOV_1 + HOUR))
        self.assertEqual(self.gaps(), [])

    def test_future_month_is_not_complete(self):
        result = self.completeness(now=OCT_1 - HOUR)
        self.assertEqual(
            result, {"complete": False, "reported_until": None, "gaps": []}
        )


class MonthCompletenessAcrossRunsTest(MonthlyUsageTestCase):
    """Gaps follow runs by run_id across keys and server instances, and close again."""

    def november(self, now=NOV_1 + timedelta(days=2)):
        result = usage.month_completeness(self.organization, 2026, 11, now=now)
        return [(gap["kind"], gap["from"], gap["to"]) for gap in result["gaps"]]

    def new_key(self, created_at):
        key = usage.register_key(
            self.organization, public_pem(ec.generate_private_key(ec.SECP256R1()))
        )
        UsageServerKey.objects.filter(pk=key.pk).update(created_at=created_at)
        key.refresh_from_db()
        return key

    def test_redeploy_under_a_new_instance_name(self):
        # The pod crashes; its replacement has another hostname, so another server_instance.
        crash, takeover = at(30, 23), at(30, 23) + timedelta(minutes=5)
        self.store(*hourly_run(at(29), crash))
        self.store(
            *hourly_run(
                takeover, NOV_1 + timedelta(days=2), "run-2", server_instance="pod-b"
            )
        )
        self.assertEqual(self.gaps(), [("interrupted", crash, takeover)])
        self.assertEqual(self.november(), [])

    def test_upgrade_from_a_server_without_heartbeat(self):
        # A 1.5.0 container is killed during the upgrade and comes back under a new name.
        self.store(
            report(1, at(29), at(29, 1), heartbeat=None),
            report(2, at(30), at(30, 1), heartbeat=None),
        )
        self.store(
            *hourly_run(
                at(30, 12), NOV_1 + timedelta(days=2), "run-2", server_instance="pod-b"
            )
        )
        self.assertEqual(self.gaps(), [("no_heartbeat", at(29), at(30, 12))])
        self.assertEqual(self.november(), [])

    def test_key_rotation_keeps_the_run(self):
        # The old key is deactivated mid-run; the server sends the rest of its run with a new
        # key, starting with the report the old key could no longer deliver.
        UsageServerKey.objects.filter(pk=self.key.pk).update(deactivated_at=at(15))
        new_key = self.new_key(at(15))
        reports = hourly_run(OCT_1 - HOUR, NOV_1 + HOUR)
        for payload in reports:
            moment = datetime.fromisoformat(payload["period"]["to"])
            usage.store_report(self.key if moment <= at(15) else new_key, payload)
        self.assertEqual(self.gaps(), [])

    def test_report_resent_under_a_new_key_counts_once(self):
        new_key = self.new_key(at(15))
        payload = report(
            1,
            at(14),
            at(14, 1),
            sessions=[("2026-10-14", "shop", "disclosing", "done", 5)],
        )
        _, created = usage.store_report(self.key, payload)
        self.assertTrue(created)
        _, created = usage.store_report(new_key, payload)
        self.assertFalse(created)
        usage_data = usage.monthly_usage(self.organization, 2026, 10)
        self.assertEqual(sum(row["count"] for row in usage_data["sessions"]), 5)

    def test_replica_that_dies_is_one_gap(self):
        # Two replicas; one dies on the 5th while the other keeps reporting.
        self.store(*hourly_run(OCT_1 - HOUR, at(5), "run-a", server_instance="pod-a"))
        self.store(
            *hourly_run(
                OCT_1 - HOUR,
                NOV_1 + timedelta(days=2),
                "run-b",
                server_instance="pod-b",
            )
        )
        # Running, it would have reported by 01:15; the other replica reported until 02:00.
        self.assertEqual(self.gaps(), [("interrupted", at(5), at(5, 2))])
        self.assertEqual(self.november(), [])

    def test_month_without_any_report_while_a_key_is_active(self):
        # Stopped cleanly in September, and nothing in October: a misconfigured restart looks
        # like this, so it must not pass as a complete month.
        self.store(
            *hourly_run(
                OCT_1 - timedelta(days=12), OCT_1 - timedelta(days=11), final=True
            )
        )
        self.assertEqual(self.gaps(), [("no_reports", OCT_1, NOV_1)])

    def test_server_without_heartbeat_registered_mid_month(self):
        # A 1.5.0 server only reports when it had sessions; its key is registered on the 15th.
        UsageServerKey.objects.filter(pk=self.key.pk).update(created_at=at(15))
        self.store(
            *(
                report(day - 2, at(day), at(day, 1), heartbeat=None)
                for day in range(3, 31)
            )
        )
        self.assertEqual(
            self.gaps(), [("no_key", OCT_1, at(3)), ("no_heartbeat", at(3), NOV_1)]
        )

    def test_crash_followed_by_lost_first_reports_is_one_gap(self):
        self.store(*hourly_run(OCT_1, at(10)))
        self.store(*hourly_run(at(10, 3), NOV_1 + HOUR, run_id="run-2", skip={1}))
        [gap] = self.completeness()["gaps"]
        self.assertEqual(
            (gap["kind"], gap["from"], gap["to"], gap["missing_count"]),
            ("missing_reports", at(10), at(10, 4), 1),
        )

    def test_number_of_queries_does_not_grow_with_runs(self):
        for day in range(2, 30):
            self.store(
                report(
                    1,
                    at(day),
                    at(day, 1),
                    run_id=f"run-{day}",
                    server_instance=f"pod-{day}",
                ),
                report(
                    2,
                    at(day, 1),
                    at(day, 2),
                    run_id=f"run-{day}",
                    server_instance=f"pod-{day}",
                    final=True,
                ),
            )
        with CaptureQueriesContext(connection) as captured:
            self.completeness()
        # The development settings' query profiler can add an EXPLAIN per query.
        queries = [q for q in captured if not q["sql"].startswith("EXPLAIN")]
        self.assertEqual(len(queries), 2)
