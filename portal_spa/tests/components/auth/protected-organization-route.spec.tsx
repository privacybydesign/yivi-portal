import { beforeAll, beforeEach, expect, it, vi } from "vitest";
import { generateJwt, renderWithRouter } from "tests/utils";
import { screen, waitFor } from "@testing-library/dom";

import useStore from "@/store";
import App from "@/App";
import { fetchOrganization } from "@/actions/manage-organization";
import { generateOrganization } from "../../utils";
import "../../mocks";

beforeAll(() => {
  vi.mock("@/actions/manage-organization");
});

beforeEach(() => {
  vi.clearAllMocks();
});

it("renders the organization management page when authorized", async () => {
  const organization = generateOrganization();
  const claims = { organizationSlugs: [organization.slug] };

  //@ts-expect-error Function is mocked.
  fetchOrganization.mockResolvedValueOnce(organization);

  useStore.getState().setAccessToken(generateJwt(claims));

  renderWithRouter(<App />, {
    route: `/organizations/${organization.slug}/manage/`,
  });

  await waitFor(() => {
    expect(screen.getByTestId("organization-management")).toBeInTheDocument();
  });
});

it("redirects to the home page when not authorized", async () => {
  useStore.getState().setAccessToken(generateJwt());

  renderWithRouter(<App />, {
    route: "/organizations/unauthorized-org/manage",
  });

  await waitFor(() => {
    expect(screen.getByText("Welcome to the Yivi Portal")).toBeInTheDocument();
  });
});
