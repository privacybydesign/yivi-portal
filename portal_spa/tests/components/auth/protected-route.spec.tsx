import { beforeEach, expect, it, vi } from "vitest";
import { renderWithRouter } from "tests/utils";
import { screen, waitFor } from "@testing-library/dom";

import App from "@/App";

import "tests/mocks";

beforeEach(() => {
  vi.clearAllMocks();
});

it("renders a heads-up message before redirecting when not authenticated", async () => {
  renderWithRouter(<App />, { route: `/organizations/register` });

  await waitFor(() => {
    expect(
      screen.getByText("You are not authenticated. Redirecting..."),
    ).toBeInTheDocument();
  });
});

it("redirects to the login page when not authenticated", async () => {
  renderWithRouter(<App />, { route: `/organizations/register` });

  await waitFor(() => {
    expect(
      screen.getByText("You are not authenticated. Redirecting..."),
    ).toBeInTheDocument();
  });
});
