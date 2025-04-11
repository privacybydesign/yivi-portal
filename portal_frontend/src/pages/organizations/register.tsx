"use client";

import { useActionState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/src/components/ui/button";
import { Input } from "@/src/components/ui/input";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from "@/src/components/ui/form";
import { Label } from "@/src/components/ui/label";
import {
  registerOrganization,
  RegistrationFormState,
  RegistrationInputs,
} from "@/src/actions/register-organization";
import { generateSlug } from "@/lib/utils";
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/src/components/ui/avatar";
import { UploadIcon, XIcon } from "lucide-react";
import { Control, UseFormSetValue, useForm, useWatch } from "react-hook-form";

const defaultFormInput: RegistrationInputs = {
  name_en: "",
  name_nl: "",
  slug: "",
  registration_number: "",
  street: "",
  housenumber: "",
  postal_code: "",
  city: "",
  country: "",
  logo: undefined,
};

export default function RegisterOrganization() {
  const [formState, register, pending] = useActionState<
    RegistrationFormState,
    FormData
  >(registerOrganization, {
    values: defaultFormInput,
    errors: {},
  });

  const router = useRouter();
  if (formState?.success && formState?.redirectTo) {
    router.push(formState.redirectTo);
  }

  const form = useForm<RegistrationInputs>({
    defaultValues: formState?.values ?? defaultFormInput,
  });

  useEffect(() => {
    form.clearErrors();
    if (formState?.errors) {
      (
        Object.entries(formState.errors) as [
          keyof RegistrationInputs,
          { message?: string }
        ][]
      ).forEach(([field, error]) => {
        if (error?.message) {
          form.setError(field, {
            type: "server",
            message: error.message,
          });
        }
      });
    }
  }, [formState?.errors, form]);

  const LogoPreview = ({
    control,
    setValue,
  }: {
    control: Control<RegistrationInputs>;
    setValue: UseFormSetValue<RegistrationInputs>;
  }) => {
    const logo = useWatch({ control, name: "logo" });

    return (
      <div className="relative size-24">
        <Avatar className="!size-24">
          <AvatarImage
            src={logo ? URL.createObjectURL(logo) : "/logo-placeholder.svg"}
            className="rounded-full border object-contain"
          />
          <AvatarFallback></AvatarFallback>
        </Avatar>

        {logo && (
          <button
            type="button"
            onClick={() => setValue("logo", undefined)}
            className="bg-red-400 rounded-full p-1 absolute top-0 right-0"
          >
            <XIcon size={12} strokeWidth={3} />
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex flex-col gap-6 mb-6">
        <h1 className="text-2xl font-bold mb-1">Register Organization</h1>
        <Form {...form}>
          <form action={register} className="space-y-4">
            <FormField
              control={form.control}
              name="logo"
              render={({ field: { onChange } }) => (
                <FormItem className="grid md:grid-cols-2 items-center md:gap-4">
                  <div className="py-1">
                    <Label className="">Organization Logo</Label>
                    <FormDescription>
                      Upload your logo (PNG or JPEG).
                    </FormDescription>
                  </div>
                  <div className="flex items-center justify-between w-full">
                    <LogoPreview {...form} />
                    <Label>
                      <div className="inline-block cursor-pointer whitespace-nowrap rounded-md text-sm font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 flex items-center gap-2">
                        <UploadIcon size={12} strokeWidth={3} />
                        Select logo
                      </div>
                      <FormControl>
                        <Input
                          type="file"
                          accept="image/png,image/jpeg"
                          className="hidden"
                          onChange={(event) =>
                            onChange(event.target.files?.[0])
                          }
                        />
                      </FormControl>
                    </Label>
                    {formState.errors.logo && (
                      <FormMessage className="text-sm text-red-600 mt-1">
                        {!formState.errors.logo.message}
                      </FormMessage>
                    )}
                  </div>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="name_en"
              render={({ field: { onBlur, ...field } }) => (
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
                          if (!form.control.getFieldState("slug").isDirty) {
                            form.setValue(
                              "slug",
                              generateSlug(event.target.value.trim())
                            );
                          }
                          onBlur();
                        }}
                      />
                    </FormControl>
                    {formState.errors.name_en && (
                      <FormMessage className="text-sm text-red-600 mt-1">
                        {!formState.errors.name_en.message}
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
                      Auto-generated from the name. Lowercase, hyphens instead
                      of spaces, no special characters.
                    </FormDescription>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} pattern="[a-z0-9\-]+" />
                    </FormControl>
                    {formState.errors.slug && (
                      <FormMessage className="text-sm text-red-600 mt-1">
                        {!formState.errors.slug.message}
                      </FormMessage>
                    )}
                  </div>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="registration_number"
              render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>Registration Number</Label>
                    <FormDescription>
                      e.g. KVK number or similar official registration code.
                    </FormDescription>
                  </div>
                  <div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    {formState.errors.registration_number && (
                      <FormMessage className="text-sm text-red-600 mt-1">
                        {!formState.errors.registration_number.message}
                      </FormMessage>
                    )}
                  </div>
                </FormItem>
              )}
            />

            <fieldset className="border border-primary-light rounded-lg p-4">
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

                      {formState.errors.registration_number && (
                        <FormMessage className="text-sm text-red-600 mt-1">
                          {!formState.errors.registration_number.message}
                        </FormMessage>
                      )}
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="housenumber"
                render={({ field }) => (
                  <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                    <div className="py-1">
                      <Label>House Number</Label>
                    </div>
                    <div>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>

                      {formState.errors.registration_number && (
                        <FormMessage className="text-sm text-red-600 mt-1">
                          {!formState.errors.registration_number.message}
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

                      {formState.errors.registration_number && (
                        <FormMessage className="text-sm text-red-600 mt-1">
                          {!formState.errors.registration_number.message}
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

                      {formState.errors.registration_number && (
                        <FormMessage className="text-sm text-red-600 mt-1">
                          {!formState.errors.registration_number.message}
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

                      {formState.errors.registration_number && (
                        <FormMessage className="text-sm text-red-600 mt-1">
                          {!formState.errors.registration_number.message}
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
      </div>
    </div>
  );
}
