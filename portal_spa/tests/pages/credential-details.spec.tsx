import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Outlet, Route, Routes } from "react-router-dom";
import CredentialDetailsPage from "@/pages/CredentialDetailsPage";
import type { Credential } from "@/models/credential";
import { Environment } from "@/models/yivi-environment";

// Chrome returns a Promise from `window.scrollTo` when smooth scrolling is
// requested, Firefox returns undefined. An effect that returns that value
// hands React a non-callable "cleanup", which throws on the next deps change
// and unmounts the entire root - a blank page on
// /attribute-index/credentials/... . jsdom has no scrollTo at all, so model
// the Chrome behaviour explicitly.
beforeEach(() => {
  vi.stubGlobal(
    "scrollTo",
    vi.fn(() => Promise.resolve()),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

const credential: Credential = {
  id: 1,
  name_en: "Address",
  name_nl: "Adres",
  ap_slug: "gemeenten",
  environment: Environment.production,
  org_name: "Gemeenten",
  org_slug: "gemeenten",
  credential_id: "address",
  description_en: "Your address",
  full_path: "pbdf.gemeente.address",
  issue_url: "https://example.org",
  attributes: [
    {
      credential_attribute_tag: "street",
      name_en: "Street",
      name_nl: "Straat",
      reason_en: "",
      reason_nl: "",
      credential_id: 1,
      optional: false,
    },
  ],
};

const page = (credentials: Credential[]) => (
  <MemoryRouter
    initialEntries={[
      "/attribute-index/credentials/production/gemeenten/address",
    ]}
  >
    <Routes>
      <Route
        path="/attribute-index"
        element={<Outlet context={{ credentials }} />}
      >
        <Route
          path="credentials/:environment/:ap_slug/:credential_id"
          element={<CredentialDetailsPage />}
        />
      </Route>
    </Routes>
  </MemoryRouter>
);

it("survives the credential arriving after the first render", () => {
  // The credentials list is fetched by the layout, so the page first renders
  // empty and re-renders once the request resolves. That changes the scroll
  // effect's dependency, which runs its cleanup.
  const { rerender } = render(page([]));

  rerender(page([credential]));

  expect(screen.getByRole("heading", { name: "Address" })).toBeInTheDocument();
  expect(window.scrollTo).toHaveBeenCalled();
});
