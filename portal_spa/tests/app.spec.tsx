import { expect, it } from "vitest";
import { generateJwt, renderWithRouter } from "tests/utils";
import App from "@/App";
import useStore from "@/store";
import { act } from "@testing-library/react";

it("should render app", () => {
  renderWithRouter(<App />);
});

it("should hide login button when logged in", () => {
  const screen = renderWithRouter(<App />);

  act(() => {
    useStore.getState().setAccessToken(generateJwt());
  });

  expect(
    screen.queryByTestId("header-login-button"),
  ).to.not.toBeInTheDocument();
});
