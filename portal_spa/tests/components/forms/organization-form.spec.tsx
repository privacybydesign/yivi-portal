import { expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import OrganizationForm from "@/components/forms/organization/OrganizationForm";
import { axiosInstance } from "@/services/axiosInstance";

const form = () => (
  <MemoryRouter>
    <OrganizationForm
      pendingButtonLabel="Registering..."
      submitButtonLabel="Register"
    />
  </MemoryRouter>
);

const submit = async () => {
  await userEvent.click(screen.getByRole("button", { name: "Register" }));
};

const emailInput = () => screen.getByLabelText("Contact Email");

const phoneInput = () =>
  screen.getByLabelText("Contact Number") as HTMLInputElement;

it("does not register an organization without contact details", async () => {
  const post = vi.spyOn(axiosInstance, "post");

  render(form());
  await submit();

  expect(
    await screen.findByText("An email address is required."),
  ).toBeInTheDocument();
  expect(screen.getByText("A phone number is required.")).toBeInTheDocument();
  expect(post).not.toHaveBeenCalled();

  post.mockRestore();
});

it("rejects a malformed email address before calling the API", async () => {
  const post = vi.spyOn(axiosInstance, "post");

  render(form());
  await userEvent.type(emailInput(), "not-an-email");
  await userEvent.type(phoneInput(), "612345678");
  await submit();

  expect(
    await screen.findByText("Enter a valid email address."),
  ).toBeInTheDocument();
  expect(post).not.toHaveBeenCalled();

  post.mockRestore();
});

it("rejects a phone input holding nothing but its dial code", async () => {
  const post = vi.spyOn(axiosInstance, "post");

  render(form());
  // The Dutch default country prefills "+31", which is not a phone number.
  expect(phoneInput().value).toMatch(/^\+31/);
  await submit();

  expect(
    await screen.findByText("A phone number is required."),
  ).toBeInTheDocument();
  expect(post).not.toHaveBeenCalled();

  post.mockRestore();
});

it("submits the form data once the contact details are filled in", async () => {
  // The action is dispatched by hand rather than through the form's `action`
  // attribute, so cover that the API is still called with the form's own
  // multipart FormData.
  const post = vi
    .spyOn(axiosInstance, "post")
    .mockResolvedValue({ data: { success: "created" } });

  render(form());
  await userEvent.type(emailInput(), "contact@test-org.example");
  await userEvent.type(phoneInput(), "612345678");
  await submit();

  // A successful registration is followed by a token refresh to pick up the
  // new organization claim, so match on the create call rather than the count.
  const createCalls = () =>
    post.mock.calls.filter(([url]) => url === "/v1/organizations/create/");
  await waitFor(() => expect(createCalls()).toHaveLength(1));

  const [, body] = createCalls()[0] as [string, FormData];
  expect(body).toBeInstanceOf(FormData);
  const formData = body;
  expect(formData.get("contact_email")).toBe("contact@test-org.example");
  expect(formData.get("contact_number")).toContain("6 12345678");

  post.mockRestore();
});
