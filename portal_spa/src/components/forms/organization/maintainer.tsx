import { useActionState, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Label } from "@/components/ui/label";
import { addMaintainerForOrganization } from "@/actions/manage-maintainer";
import type {
  RegistrationFormState,
  MaintainerRegistrationInputs,
} from "@/actions/manage-maintainer";
import type { Organization } from "@/models/organization";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";

export default function AddOrganizationMaintainerInformationForm({
  organization,
  onCreate,
}: {
  organization: Organization;
  onCreate: (organisationSlug: string) => unknown;
}) {
  const { t } = useTranslation();

  const [defaultFormInput] = useState({
    email: "",
    organizationSlug: organization.slug,
  } as MaintainerRegistrationInputs);
  const [modalIsOpen, setModalIsOpen] = useState(false);

  const [formState, formSubmit, pending] = useActionState<
    RegistrationFormState,
    FormData
  >(addMaintainerForOrganization, {
    values: defaultFormInput,
    errors: {},
  });

  const form = useForm<MaintainerRegistrationInputs>({
    defaultValues: defaultFormInput,
  });

  useEffect(() => {
    form.clearErrors();

    if (formState?.errors) {
      Object.entries(formState.errors).forEach(([field, error]) => {
        if (error?.message) {
          form.setError(field as keyof MaintainerRegistrationInputs, {
            type: "server",
            message: error.message,
          });
        }
      });
    }
  }, [formState?.errors, form]);

  useEffect(() => {
    if (formState.success) {
      setModalIsOpen(false);
      onCreate(organization.slug);

      toast.success("Success", {
        description: "The user was created and added to this organization.",
      });

      // Will prevent the dialog from closing directly when opened again.
      formState.success = false;
      form.reset();
    }
  }, [form, formState, organization, onCreate]);

  return (
    <Dialog open={modalIsOpen} onOpenChange={setModalIsOpen}>
      <DialogTrigger className={cn(buttonVariants())}>
        {t("maintainer_form.add_button")}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("maintainer_form.title")}</DialogTitle>
          <DialogDescription>
            {t("maintainer_form.description")}{" "}
            <ul className="list-disc pl-5">
              <li>{t("maintainer_form.permission_modify")}</li>
              <li>{t("maintainer_form.permission_rp")}</li>
              <li>{t("maintainer_form.permission_maintainers")}</li>
            </ul>
            <p className="mt-2">{t("maintainer_form.confirmation")}</p>
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form action={formSubmit} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-x-4">
                  <div className="py-1 space-y-0.5">
                    <Label>{t("maintainer_form.email_label")}</Label>
                    <FormDescription>
                      {t("maintainer_form.email_description")}
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Input type="email" {...field} />
                  </FormControl>
                  {formState.errors.email && (
                    <FormMessage className="col-span-2 text-sm text-red-600 mt-1">
                      {!formState.errors.email.message}
                    </FormMessage>
                  )}
                </FormItem>
              )}
            />

            {formState?.globalError && (
              <div className="col-span-2 text-sm text-red-600 font-medium">
                {formState.globalError}
              </div>
            )}

            <div className="flex sm:justify-end">
              <Button type="submit" disabled={pending} className="col-span-2">
                {pending ? t("generic.submitting") : t("generic.submit")}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
