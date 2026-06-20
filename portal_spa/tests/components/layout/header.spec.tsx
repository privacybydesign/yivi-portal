import { expect, it } from "vitest";
import Header from "@/components/layout/Header";
import { renderWithRouter } from "tests/utils";
import { screen } from "@testing-library/dom";

// Regression test for the menu overlapping the logo on narrow viewports
// (issue #294). The nav must be allowed to wrap and the logo must not shrink,
// so the menu group drops below the logo instead of overlapping it.
it("lets the navigation wrap so the menu cannot overlap the logo", () => {
  renderWithRouter(<Header />);

  const logo = screen.getByAltText("Yivi Logo");
  const nav = logo.closest("nav");
  expect(nav).not.toBeNull();
  expect(nav).toHaveClass("flex-wrap");

  const logoLink = logo.closest("a");
  expect(logoLink).toHaveClass("shrink-0");
});
