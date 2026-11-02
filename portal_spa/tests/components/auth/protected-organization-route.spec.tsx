import { beforeEach, expect, it, vi } from "vitest";
import { generateJwt, renderWithRouter } from "tests/utils";
import { screen, waitFor } from "@testing-library/dom";

import useStore from "@/store";
import App from "@/App";
import { generateOrganization } from "tests/utils";
import "tests/mocks";
import { setRefreshResponse } from "tests/mocks/api";

beforeEach(() => {
  vi.clearAllMocks();
});

it("renders the organization management page when authorized", async () => {
  const organization = generateOrganization();
  const claims = { organizationSlugs: [organization.slug] };

  // The session is restored from the refresh cookie on load, so the refreshed
  // token must carry the maintainer's organization membership.
  setRefreshResponse(200, claims);
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
