import { useActionState, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { registerOrganization } from "@/actions/manage-organization";
import type {
  RegistrationFormState,
  RegistrationInputs,
} from "@/actions/manage-organization";
import { useForm } from "react-hook-form";
import { updateOrganization } from "@/actions/manage-organization";
import type { Organization } from "@/models/organization";
import { useNavigate } from "react-router-dom";
import OrganizationNameFields from "./child-components/OrganizationNameFields";
import LogoUpload from "./child-components/LogoUpload";
import ContactFields from "./child-components/ContactFields";
import SlugField from "./child-components/SlugField";
import ContactAddressBox from "./child-components/ContactAddressBox";

export default function OrganizationForm({
  organization,
  editMode,
}: {
  organization?: Organization;
  editMode: boolean;
}) {
  const [defaultFormInput] = useState({
    name_en: "",
    name_nl: "",
    slug: "",
    street: "",
    house_number: "",
    postal_code: "",
    city: "",
    country: "NL",
    contact_number: "",
    ...(organization || {}),
  } as RegistrationInputs);

  const [cachedLogo, setCachedLogo] = useState<File | null>(null);

  const navigate = useNavigate();

  const [formState, formSubmit, pending] = useActionState<
    RegistrationFormState,
    FormData
  >(organization ? updateOrganization : registerOrganization, {
    values: defaultFormInput,
    errors: {},
  });

  if (formState?.success && formState?.redirectTo) {
    navigate(formState.redirectTo);
  }

  const form = useForm<RegistrationInputs>({
    defaultValues: defaultFormInput,
  });

  useEffect(() => {
    form.reset(organization);
  }, [organization, form]);

  useEffect(() => {
    form.clearErrors();

    if (formState?.errors) {
      Object.entries(formState.errors).forEach(([field, error]) => {
        if (error?.message) {
          form.setError(field as keyof RegistrationInputs, {
            type: "server",
            message: error.message,
          });
        }
      });
    }
  }, [formState?.errors, form]);

  const submitWithLogo = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    if (!data.get("logo") && cachedLogo) {
      data.set("logo", cachedLogo);
    }
    formSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={submitWithLogo} className="space-y-4">
        <LogoUpload
          form={form}
          formState={formState}
          cachedLogo={cachedLogo}
          setCachedLogo={setCachedLogo}
        />

        <OrganizationNameFields form={form} formState={formState} />

        <SlugField form={form} formState={formState} />

        <ContactFields form={form} formState={formState} />

        <ContactAddressBox form={form} formState={formState} />

        <Button type="submit" disabled={pending} className="col-span-2">
          {pending
            ? editMode
              ? "Saving..."
              : "Submitting..."
            : editMode
            ? "Save"
            : "Submit"}
        </Button>

        {formState?.globalError && (
          <div className="col-span-2 text-sm text-red-600 font-medium">
            {formState.globalError}
          </div>
        )}
      </form>
    </Form>
  );
}
