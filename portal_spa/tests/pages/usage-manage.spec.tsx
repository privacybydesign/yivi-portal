import { afterEach, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import UsageManagePage from "@/pages/UsageManagePage";
import { OrganizationContext } from "@/contexts/organization/OrganizationContext";
import { axiosInstance } from "@/services/axiosInstance";

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

const monthlyUsage = {
  month: "2026-11",
  actions: ["disclosing", "signing"],
  outcomes: ["done"],
  sessions: [
    { requestor: "webshop", action: "disclosing", outcome: "done", count: 7 },
  ],
  credentials: [
    {
      requestor: "webshop",
      action: "disclosing",
      outcome: "done",
      credential_type: "pbdf.pbdf.idin",
      count: 5,
    },
    {
      requestor: "webshop",
      action: "disclosing",
      outcome: "done",
      credential_type: "pbdf.sidn-pbdf.email",
      count: 4,
    },
  ],
  completeness: {
    complete: false,
    reported_until: "2026-11-02T10:00:00Z",
    gaps: [
      {
        kind: "missing_reports",
        from: "2026-11-01T04:00:00Z",
        to: "2026-11-01T06:00:00Z",
        server_instance: "irma-prod-1",
        missing_count: 2,
      },
    ],
  },
};

const mockApi = (verified: boolean) =>
  vi.spyOn(axiosInstance, "get").mockImplementation(async (url: string) => {
    if (url === "/v1/organizations/webshop/") {
      return { data: { slug: "webshop", is_verified: verified } };
    }
    if (url === "/v1/organizations/webshop/usage-keys/") {
      return {
        data: [
          {
            id: "k1",
            label: "production server",
            thumbprint: "abc123",
            created_at: "2026-10-30T10:00:00Z",
            deactivated_at: null,
            is_active: true,
          },
        ],
      };
    }
    if (url === "/v1/organizations/webshop/usage/") {
      return {
        data: {
          sessions: [
            {
              day: "2026-11-01",
              requestor: "a",
              action: "disclosing",
              outcome: "done",
              count: 1200,
            },
            {
              day: "2026-11-02",
              requestor: "a",
              action: "disclosing",
              outcome: "done",
              count: 34,
            },
            {
              day: "2026-11-02",
              requestor: "a",
              action: "disclosing",
              outcome: "cancelled",
              count: 9,
            },
          ],
          gaps: [],
        },
      };
    }
    if (url === "/v1/organizations/webshop/usage/monthly/") {
      return { data: monthlyUsage };
    }
    throw new Error(`unexpected GET ${url}`);
  });

const renderPage = () =>
  render(
    <OrganizationContext.Provider value={{ webshop: "Webshop" }}>
      <MemoryRouter initialEntries={["/organizations/webshop/manage/usage"]}>
        <Routes>
          <Route
            path="/organizations/:organization/manage/usage"
            element={<UsageManagePage />}
          />
        </Routes>
      </MemoryRouter>
    </OrganizationContext.Provider>,
  );

it("shows the current calendar month's successful verifications and the keys", async () => {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date(2026, 10, 2, 12));
  const get = mockApi(true);

  renderPage();

  expect(await screen.findByText("1,234")).toBeInTheDocument();
  expect(screen.getByText("Total in November 2026")).toBeInTheDocument();
  expect(get).toHaveBeenCalledWith("/v1/organizations/webshop/usage/", {
    params: { from: "2026-11-01", to: "2026-11-30" },
  });
  const chart = screen.getByRole("group", {
    name: "Successful verifications per day in November 2026",
  });
  expect(within(chart).getAllByRole("button")).toHaveLength(30);
  expect(
    within(chart).getByRole("button", {
      name: "2 November 2026: 34 successful verifications",
    }),
  ).toBeInTheDocument();
  expect(await screen.findByText("production server")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Next month" })).toBeDisabled();
});

it("offers no key registration before the organization is verified", async () => {
  const get = mockApi(false);

  renderPage();

  expect(
    await screen.findByText(
      /becomes available once your organization is verified/,
    ),
  ).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Register key" })).toBeNull();
  expect(get).not.toHaveBeenCalledWith("/v1/organizations/webshop/usage-keys/");
});

it("does not call a verified organization unverified when it fails to load", async () => {
  vi.spyOn(axiosInstance, "get").mockRejectedValue(new Error("network down"));
  vi.spyOn(console, "error").mockImplementation(() => {});

  renderPage();

  expect(
    await screen.findByText(/organization could not be loaded/),
  ).toBeInTheDocument();
  expect(
    screen.queryByText(/becomes available once your organization is verified/),
  ).toBeNull();
});

it("clears a period's load error once another period loads", async () => {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date(2026, 10, 2, 12));
  const get = mockApi(true);
  const failOnce = get.getMockImplementation()!;
  get.mockImplementation(async (url: string, config?: unknown) => {
    const params = (config as { params?: { from: string } } | undefined)
      ?.params;
    if (
      url === "/v1/organizations/webshop/usage/" &&
      params?.from === "2026-11-01"
    ) {
      throw new Error("500");
    }
    return failOnce(url, config as never);
  });

  renderPage();

  expect(
    await screen.findByText(/Usage could not be loaded/),
  ).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Previous month" }));
  expect(await screen.findByText("Total in October 2026")).toBeInTheDocument();
  expect(screen.queryByText(/Usage could not be loaded/)).toBeNull();
});

it("breaks the month down per requestor and credential type, with its gaps", async () => {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date(2026, 10, 2, 12));
  const get = mockApi(true);

  renderPage();

  const section = await screen.findByRole("region", {
    name: "Usage per credential type",
  });
  // Seven sessions, nine credentials: sessions are never summed from credentials.
  expect(await within(section).findByText("9")).toBeInTheDocument();
  expect(within(section).getAllByText("7").length).toBeGreaterThan(0);
  expect(
    within(section).getByRole("table", {
      name: "Sessions and credentials per requestor in November 2026",
    }),
  ).toBeInTheDocument();
  expect(within(section).getAllByText("pbdf.pbdf.idin")).toHaveLength(2);
  expect(within(section).getByRole("alert")).toHaveTextContent(
    "1 Nov, 04:00 – 1 Nov, 06:00 UTC: irma-prod-1: 2 reports did not arrive.",
  );
  expect(get).toHaveBeenCalledWith("/v1/organizations/webshop/usage/monthly/", {
    params: {
      month: "2026-11",
      action: ["disclosing", "signing"],
      outcome: ["done"],
    },
    paramsSerializer: { indexes: null },
  });

  // Other outcomes on request, and back to what is invoiced.
  await userEvent.click(within(section).getByRole("button", { name: "Timed out" }));
  expect(get).toHaveBeenCalledWith(
    "/v1/organizations/webshop/usage/monthly/",
    expect.objectContaining({
      params: expect.objectContaining({ outcome: ["done", "timeout"] }),
    }),
  );
  await userEvent.click(
    within(section).getByRole("button", { name: "Show what is invoiced" }),
  );
  expect(
    within(section).getByRole("button", { name: "Timed out" }),
  ).toHaveAttribute("aria-pressed", "false");
  // The last selected outcome cannot be switched off.
  expect(within(section).getByRole("button", { name: "Done" })).toBeDisabled();
});

it("downloads the month as CSV", async () => {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date(2026, 10, 2, 12));
  const get = mockApi(true);
  const answer = get.getMockImplementation()!;
  get.mockImplementation(async (url: string, config?: unknown) =>
    url === "/v1/organizations/webshop/usage/monthly/csv/"
      ? { data: new Blob(["month"], { type: "text/csv" }) }
      : answer(url, config as never),
  );
  URL.createObjectURL = vi.fn(() => "blob:usage");
  URL.revokeObjectURL = vi.fn();
  const click = vi
    .spyOn(HTMLAnchorElement.prototype, "click")
    .mockImplementation(() => {});

  renderPage();

  await userEvent.click(
    await screen.findByRole("button", { name: "Download CSV" }),
  );
  expect(get).toHaveBeenCalledWith(
    "/v1/organizations/webshop/usage/monthly/csv/",
    expect.objectContaining({ responseType: "blob" }),
  );
  expect(click).toHaveBeenCalled();
  expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:usage");
});
