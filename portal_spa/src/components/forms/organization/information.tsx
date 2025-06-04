import { useActionState, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Label } from "@/components/ui/label";
import { registerOrganization } from "@/actions/manage-organization";
import type {
  RegistrationFormState,
  RegistrationInputs,
} from "@/actions/manage-organization";
import { generateSlug } from "@/lib/utils";
import { UploadIcon } from "lucide-react";
import { useForm } from "react-hook-form";
import { updateOrganization } from "@/actions/manage-organization";
import type { Organization } from "@/models/organization";
import { LogoPreview } from "@/components/ui/logo-preview";
import { useNavigate } from "react-router-dom";

export default function ManageOrganizationInformationForm({
  organization,
}: {
  organization?: Organization;
}) {
  const [defaultFormInput] = useState({
    name_en: "",
    name_nl: "",
    slug: "",
    street: "",
    house_number: "",
    postal_code: "",
    city: "",
    country: "",
    logo: undefined,
    ...(organization || {}),
  } as RegistrationInputs);

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

  return (
    <Form {...form}>
      <form action={formSubmit} className="space-y-4">
        <FormField
          control={form.control}
          name="logo"
          render={({ field: { onChange, value, ...field } }) => (
            <FormItem className="grid md:grid-cols-2 items-center md:gap-4">
              <div className="py-1">
                <Label>Organization Logo</Label>
                <FormDescription>
                  Upload your logo (PNG or JPEG).
                </FormDescription>
              </div>
              <div className="flex flex-col items-start w-full">
                <div className="flex items-center justify-between w-full">
                  <LogoPreview
                    control={form.control}
                    setValue={form.setValue}
                    name={typeof value === "string" ? value : value?.name}
                  />
                  <Label>
                    <div className="cursor-pointer whitespace-nowrap rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 flex items-center gap-2">
                      <UploadIcon size={12} strokeWidth={3} />
                      Select logo
                    </div>
                    <FormControl>
                      <Input
                        type="file"
                        accept="image/png,image/jpeg"
                        className="hidden"
                        onChange={(event) => onChange(event.target.files?.[0])}
                        {...field}
                      />
                    </FormControl>
                  </Label>
                </div>
                {formState.errors.logo && (
                  <FormMessage className="text-sm text-red-600 mt-1">
                    {formState.errors.logo.message}
                  </FormMessage>
                )}
              </div>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="name_en"
          render={({ field: { ...field } }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>English Name</Label>
                <FormDescription>
                  Formal name of your organization in English.
                </FormDescription>
              </div>
              <div>
                <FormControl>
                  <Input
                    {...field}
                    onBlur={(event) => {
                      if (!form.getValues("slug")) {
                        form.setValue(
                          "slug",
                          generateSlug(event.target.value.trim())
                        );
                      }
                    }}
                  />
                </FormControl>
                {formState.errors.name_en && (
                  <FormMessage className="text-sm text-red-600">
                    {formState.errors.name_en.message}
                  </FormMessage>
                )}
              </div>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="name_nl"
          render={({ field }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>Dutch Name</Label>
                <FormDescription>
                  Formal name of your organization in Dutch.
                </FormDescription>
              </div>
              <div>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                {formState.errors.name_nl && (
                  <FormMessage className="text-sm text-red-600 mt-1">
                    {!formState.errors.name_nl.message}
                  </FormMessage>
                )}
              </div>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="slug"
          render={({ field }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>Slug</Label>
                <FormDescription>
                  Auto-generated from the name if left empty. Lowercase, hyphens
                  instead of spaces, no special characters.
                </FormDescription>
              </div>
              <div>
                <FormControl>
                  <Input
                    {...field}
                    pattern="[a-z0-9\-]+"
                    onBlur={(event) => {
                      if (!event.target.value && form.getValues("name_en")) {
                        const newSlug = generateSlug(
                          form.getValues("name_en").trim()
                        );
                        form.setValue("slug", newSlug);
                      }
                    }}
                  />
                </FormControl>
                {formState.errors.slug && (
                  <FormMessage className="text-sm text-red-600 mt-1">
                    {formState.errors.slug.message}
                  </FormMessage>
                )}
              </div>
            </FormItem>
          )}
        />

        <fieldset className="border border-primary-light rounded-lg p-4 space-y-2">
          <legend className="font-medium">Contact Address</legend>

          <FormField
            control={form.control}
            name="street"
            render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Street</Label>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>

                  {formState.errors.street && (
                    <FormMessage className="text-sm text-red-600 mt-1">
                      {!formState.errors.street.message}
                    </FormMessage>
                  )}
                </div>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="house_number"
            render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>House Number</Label>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>

                  {formState.errors.house_number && (
                    <FormMessage className="text-sm text-red-600 mt-1">
                      {!formState.errors.house_number.message}
                    </FormMessage>
                  )}
                </div>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="postal_code"
            render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Postal Code</Label>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>

                  {formState.errors.postal_code && (
                    <FormMessage className="text-sm text-red-600 mt-1">
                      {!formState.errors.postal_code.message}
                    </FormMessage>
                  )}
                </div>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="city"
            render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>City</Label>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>

                  {formState.errors.city && (
                    <FormMessage className="text-sm text-red-600 mt-1">
                      {!formState.errors.city.message}
                    </FormMessage>
                  )}
                </div>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="country"
            render={({ field }) => (
              <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                <div className="py-1">
                  <Label>Country</Label>
                </div>
                <div>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>

                  {formState.errors.country && (
                    <FormMessage className="text-sm text-red-600 mt-1">
                      {!formState.errors.country.message}
                    </FormMessage>
                  )}
                </div>
              </FormItem>
            )}
          />
        </fieldset>

        <Button type="submit" disabled={pending} className="col-span-2">
          {pending ? "Submitting..." : "Submit"}
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
