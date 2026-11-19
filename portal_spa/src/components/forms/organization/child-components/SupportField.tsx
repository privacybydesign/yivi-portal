import type { RegistrationInputs } from "@/actions/manage-organization";
import {
  FormControl,
  FormField,
  FormItem,
  FormDescription,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import type { UseFormReturn } from "react-hook-form";
import { EMAIL_PATTERN } from "./ContactField";

// The Yivi app opens the support page for its users, so only an https link.
const isHttpsUrl = (value: string) => {
  try {
    const url = new URL(value.trim());
    return url.protocol === "https:" && url.hostname.includes(".");
  } catch {
    return false;
  }
};

/**
 * Where users of the Yivi app reach the organization's own support. Both
 * fields are optional and, unlike the contact details, public.
 */
export default function SupportField({
  form,
}: {
  form: UseFormReturn<RegistrationInputs>;
}) {
  return (
    <>
      <FormField
        control={form.control}
        name="support_email"
        rules={{
          pattern: {
            value: EMAIL_PATTERN,
            message: "Enter a valid email address.",
          },
        }}
        render={({ field, fieldState }) => (
          <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
            <div className="py-1">
              <FormLabel>Support Email</FormLabel>
              <FormDescription>
                Optional. Where users of the Yivi app can ask your organization
                for help, such as your customer service. This address is
                public: it becomes visible in the Yivi app once Yivi has
                published it.
              </FormDescription>
            </div>
            <div>
              <FormControl>
                <Input type="email" {...field} value={field.value ?? ""} />
              </FormControl>
              {fieldState.error && (
                <FormMessage className="text-sm text-red-600 mt-1">
                  {fieldState.error.message}
                </FormMessage>
              )}
            </div>
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="support_url"
        rules={{
          validate: (value) =>
            !value ||
            isHttpsUrl(value) ||
            "Enter a link that starts with https://.",
        }}
        render={({ field, fieldState }) => (
          <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
            <div className="py-1">
              <FormLabel>Support Page</FormLabel>
              <FormDescription>
                Optional. A page where users of the Yivi app find help from
                your organization. It becomes visible in the Yivi app as well.
              </FormDescription>
            </div>
            <div>
              <FormControl>
                <Input
                  type="url"
                  placeholder="https://"
                  {...field}
                  value={field.value ?? ""}
                />
              </FormControl>
              {fieldState.error && (
                <FormMessage className="text-sm text-red-600 mt-1">
                  {fieldState.error.message}
                </FormMessage>
              )}
            </div>
          </FormItem>
        )}
      />
    </>
  );
}
