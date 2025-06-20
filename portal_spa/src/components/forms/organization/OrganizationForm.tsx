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
import ContactField from "./child-components/ContactField";
import SlugField from "./child-components/SlugField";
import ContactAddressBox from "./child-components/ContactAddressBox";

export default function OrganizationForm({
  organization,
  pendingButtonLabel,
  submitButtonLabel,
}: {
  organization?: Organization;
  pendingButtonLabel: string;
  submitButtonLabel: string;
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
    cachedLogo,
  });

  useEffect(() => {
    if (formState && formState.cachedLogo !== cachedLogo) {
      formState.cachedLogo = cachedLogo;
    }
  }, [cachedLogo, formState]);

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

  return (
    <Form {...form}>
      <form action={formSubmit} className="space-y-4">
        <LogoUpload
          form={form}
          formState={formState}
          cachedLogo={cachedLogo}
          setCachedLogo={setCachedLogo}
        />

        <OrganizationNameFields form={form} formState={formState} />

        <SlugField form={form} formState={formState} />

        <ContactField form={form} formState={formState} />

        <ContactAddressBox form={form} formState={formState} />

        <Button type="submit" disabled={pending} className="col-span-2">
          {pending ? pendingButtonLabel : submitButtonLabel}
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
