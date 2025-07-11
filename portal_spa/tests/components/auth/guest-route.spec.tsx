import { beforeEach, expect, it, vi } from "vitest";
import { generateJwt, renderWithRouter } from "tests/utils";
import { screen, waitFor } from "@testing-library/dom";

import "tests/mocks";

import useStore from "@/store";
import App from "@/App";

beforeEach(() => {
  vi.clearAllMocks();
});

it("renders the login page when not authenticated", async () => {
  renderWithRouter(<App />, { route: "/login" });

  await waitFor(() => {
    expect(screen.getByTestId("yivi-web-form")).toBeInTheDocument();
  });
});

it("redirects to the homepage when already authenticated", async () => {
  useStore.getState().setAccessToken(generateJwt());

  renderWithRouter(<App />, { route: "/login" });

  await waitFor(() => {
    expect(screen.queryByTestId("yivi-web-form")).not.toBeInTheDocument();
  });
});
