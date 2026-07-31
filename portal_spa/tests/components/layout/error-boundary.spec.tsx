import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ErrorBoundary from "@/components/layout/ErrorBoundary";

// React logs the caught error itself, which would otherwise clutter the run.
beforeEach(() => {
  vi.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
  vi.restoreAllMocks();
});

function Boom(): React.ReactNode {
  throw new Error("kaboom");
}

it("shows a fallback instead of unmounting the whole tree", () => {
  render(
    <MemoryRouter>
      <div>Still here</div>
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>
    </MemoryRouter>,
  );

  expect(screen.getByTestId("error-boundary-fallback")).toBeInTheDocument();
  expect(screen.getByText("Still here")).toBeInTheDocument();
});

it("clears the fallback when the reset key changes", () => {
  const { rerender } = render(
    <MemoryRouter>
      <ErrorBoundary resetKey="/broken">
        <Boom />
      </ErrorBoundary>
    </MemoryRouter>,
  );

  expect(screen.getByTestId("error-boundary-fallback")).toBeInTheDocument();

  rerender(
    <MemoryRouter>
      <ErrorBoundary resetKey="/working">
        <div>Working page</div>
      </ErrorBoundary>
    </MemoryRouter>,
  );

  expect(
    screen.queryByTestId("error-boundary-fallback"),
  ).not.toBeInTheDocument();
  expect(screen.getByText("Working page")).toBeInTheDocument();
});
