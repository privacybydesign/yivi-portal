import { expect, it } from "vitest";
import Header from "@/components/layout/Header";
import { renderWithRouter } from "tests/utils";
import { screen } from "@testing-library/dom";

// Regression tests for the menu overlapping the logo on narrow viewports
// (issue #294). Below the `sm` breakpoint the inline nav links are hidden and
// replaced by a hamburger menu, so the menu can never overlap the logo.
// jsdom does not apply media queries, so the responsive visibility is
// asserted through the Tailwind classes.

it("hides the inline nav links below the sm breakpoint", () => {
  renderWithRouter(<Header />);

  const inlineLinks = screen.getByRole("link", { name: "Organizations" });
  expect(inlineLinks.parentElement).toHaveClass("hidden", "sm:flex");
});

it("shows a hamburger menu with the nav links below the sm breakpoint", async () => {
  const { user } = renderWithRouter(<Header />);

  const trigger = screen.getByRole("button", {
    name: "Open navigation menu",
  });
  expect(trigger).toHaveClass("sm:hidden");

  await user.click(trigger);

  expect(
    await screen.findByRole("menuitem", { name: "Organizations" }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("menuitem", { name: "Attribute Index" }),
  ).toBeInTheDocument();
});
