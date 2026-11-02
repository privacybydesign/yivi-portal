import { expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AddOrganizationMaintainerInformationForm from "@/components/forms/organization/maintainer";
import type { Organization } from "@/models/organization";
import { axiosInstance } from "@/services/axiosInstance";

const organization = { slug: "webshop", name_en: "Webshop" } as Organization;

it("closes after adding a maintainer, and stays open when opened again", async () => {
  const post = vi.spyOn(axiosInstance, "post").mockResolvedValue({ data: {} });
  const onCreate = vi.fn();

  render(
    <AddOrganizationMaintainerInformationForm
      organization={organization}
      onCreate={onCreate}
    />,
  );

  await userEvent.click(screen.getByRole("button", { name: "Add maintainer" }));
  await userEvent.type(
    screen.getByRole("textbox"),
    "new.maintainer@webshop.example",
  );
  await userEvent.click(screen.getByRole("button", { name: "Submit" }));

  await waitFor(() => expect(onCreate).toHaveBeenCalledWith("webshop"));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());

  // A leftover success flag used to close the dialog again right away.
  await userEvent.click(screen.getByRole("button", { name: "Add maintainer" }));
  expect(await screen.findByRole("dialog")).toBeInTheDocument();
  await new Promise((resolve) => setTimeout(resolve, 50));
  expect(screen.getByRole("dialog")).toBeInTheDocument();
  expect(onCreate).toHaveBeenCalledTimes(1);

  post.mockRestore();
});
