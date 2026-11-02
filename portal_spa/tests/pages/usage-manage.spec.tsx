import { afterEach, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import UsageManagePage from "@/pages/UsageManagePage";
import { OrganizationContext } from "@/contexts/organization/OrganizationContext";
import { axiosInstance } from "@/services/axiosInstance";

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

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
