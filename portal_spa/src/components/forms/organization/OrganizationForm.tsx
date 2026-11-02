import {
  startTransition,
  useActionState,
  useEffect,
  useRef,
  useState,
} from "react";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import {
  addCachedLogoToFormData,
  registerOrganization,
} from "@/actions/manage-organization";
import type {
  RegistrationFormState,
  RegistrationInputs,
} from "@/actions/manage-organization";
import { useForm } from "react-hook-form";
import { updateOrganization } from "@/actions/manage-organization";
import type { Organization } from "@/models/organization";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
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
    contact_email: "",
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

  // Navigating from the render body re-runs the render it was called from, so
  // the redirect after a successful submit belongs in an effect.
  useEffect(() => {
    if (formState?.success && formState?.redirectTo) {
      navigate(formState.redirectTo);
    }
  }, [formState?.success, formState?.redirectTo, navigate]);

  // Every submit yields a new form state, so compare by identity to confirm
  // each save exactly once, also when the same details are saved twice. A new
  // registration needs no toast: it moves on to the organization's own page.
  const confirmedState = useRef<RegistrationFormState | null>(null);
  useEffect(() => {
    if (
      organization &&
      formState?.success &&
      formState !== confirmedState.current
    ) {
      confirmedState.current = formState;
      toast.success("Saved", {
        description: "Your organization's details have been saved.",
      });
    }
  }, [formState, organization]);

  const form = useForm<RegistrationInputs>({
    defaultValues: defaultFormInput,
  });

  // The action is dispatched by hand instead of through the form's `action`
  // attribute: react-hook-form validates asynchronously, so a React action
  // would already be on its way before the required contact details are
  // checked. handleSubmit blocks the submit event itself and only calls back
  // once every field passes, and the API still receives the multipart
  // FormData of the form element (the logo is a file).
  const handleSubmit = form.handleSubmit((_, event) => {
    const formElement = event?.target;
    if (formElement instanceof HTMLFormElement) {
      const formData = new FormData(formElement);
      addCachedLogoToFormData(formData, cachedLogo);
      // Dispatching outside a transition leaves `pending` stuck on false.
      startTransition(() => formSubmit(formData));
    }
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
      <form
        onSubmit={handleSubmit}
        // Field errors are rendered inline, so keep the browser from stepping
        // in front of them with its own bubbles for type="email" and friends.
        noValidate
        className="space-y-4"
      >
        <LogoUpload
          form={form}
          formState={formState}
          cachedLogo={cachedLogo}
          setCachedLogo={setCachedLogo}
        />

        <OrganizationNameFields form={form} formState={formState} />

        <SlugField form={form} formState={formState} />

        <ContactField form={form} />

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
