import { describe, expect, it } from "vitest";
import {
  BILLED_FILTER,
  credentialTypeTotals,
  gapDescription,
  gapPeriod,
  isBilledFilter,
  monthParam,
  requestorBreakdown,
  type MonthlyUsage,
  type RequestorUsage,
} from "@/actions/usage";

const usage: MonthlyUsage = {
  month: "2026-10",
  actions: ["disclosing", "signing"],
  outcomes: ["done"],
  // Three webshop sessions; one of them disclosed email, iDIN and personal data.
  sessions: [
    { requestor: "bank", action: "signing", outcome: "done", count: 1 },
    { requestor: "webshop", action: "disclosing", outcome: "done", count: 3 },
  ],
  credentials: [
    {
      requestor: "bank",
      action: "signing",
      outcome: "done",
      credential_type: "pbdf.pbdf.idin",
      count: 1,
    },
    {
      requestor: "webshop",
      action: "disclosing",
      outcome: "done",
      credential_type: "pbdf.gemeente.personalData",
      count: 1,
    },
    {
      requestor: "webshop",
      action: "disclosing",
      outcome: "done",
      credential_type: "pbdf.pbdf.idin",
      count: 2,
    },
    {
      requestor: "webshop",
      action: "disclosing",
      outcome: "done",
      credential_type: "pbdf.sidn-pbdf.email",
      count: 3,
    },
  ],
  completeness: { complete: true, reported_until: null, gaps: [] },
};

describe("requestorBreakdown", () => {
  it("counts sessions from the session counts, not from the credentials", () => {
    const [webshop, bank] = requestorBreakdown(usage) as [
      RequestorUsage,
      RequestorUsage,
    ];
    expect(webshop.requestor).toBe("webshop");
    expect(webshop.sessions).toBe(3);
    expect(webshop.credentials).toEqual([
      { credentialType: "pbdf.sidn-pbdf.email", count: 3 },
      { credentialType: "pbdf.pbdf.idin", count: 2 },
      { credentialType: "pbdf.gemeente.personalData", count: 1 },
    ]);
    expect(bank).toEqual({
      requestor: "bank",
      sessions: 1,
      credentials: [{ credentialType: "pbdf.pbdf.idin", count: 1 }],
    });
  });

  it("sums actions and outcomes of one requestor", () => {
    const [webshop] = requestorBreakdown({
      ...usage,
      sessions: [
        ...usage.sessions,
        { requestor: "webshop", action: "signing", outcome: "done", count: 2 },
      ],
    }) as [RequestorUsage];
    expect(webshop.sessions).toBe(5);
  });
});

describe("credentialTypeTotals", () => {
  it("sums each credential type over all requestors", () => {
    expect(credentialTypeTotals(usage)).toEqual([
      { credentialType: "pbdf.pbdf.idin", count: 3 },
      { credentialType: "pbdf.sidn-pbdf.email", count: 3 },
      { credentialType: "pbdf.gemeente.personalData", count: 1 },
    ]);
  });
});

describe("filters and gaps", () => {
  it("knows the invoiced selection", () => {
    expect(isBilledFilter(BILLED_FILTER)).toBe(true);
    expect(
      isBilledFilter({ actions: ["disclosing"], outcomes: ["done"] }),
    ).toBe(false);
    expect(monthParam({ kind: "month", year: 2026, month: 3 })).toBe("2026-03");
  });

  it("describes a gap in UTC", () => {
    const gap = {
      kind: "missing_reports" as const,
      from: "2026-10-01T04:00:00Z",
      to: "2026-10-01T06:00:00Z",
      server_instance: "irma-prod-1",
      missing_count: 2,
    };
    expect(gapPeriod(gap)).toBe("1 Oct, 04:00 – 1 Oct, 06:00 UTC");
    expect(gapDescription(gap)).toBe("irma-prod-1: 2 reports did not arrive.");
  });
});
