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

export default function AddOrganizationMaintainerInformationForm({
  organization,
  onCreate,
}: {
  organization: Organization;
  onCreate: (organisationSlug: string) => unknown;
}) {
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
        Add maintainer
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add maintainer</DialogTitle>
          <DialogDescription>
            This person will get the following permissions:
            <ul className="list-disc pl-5">
              <li>
                Can modify organization's information such as name and logo
              </li>
              <li>Can add/remove a relying party</li>
              <li>Can add/remove other maintainers</li>
            </ul>
            <p className="mt-2">
              The maintainer will receive an email with a confirmation that they
              have been added to this organization as a maintainer. Next time
              they log in using that email address, they will be able to manage
              this organization.
            </p>
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
                    <Label>Email address</Label>
                    <FormDescription>
                      Email address of the maintainer
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
                {pending ? "Submitting..." : "Submit"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
