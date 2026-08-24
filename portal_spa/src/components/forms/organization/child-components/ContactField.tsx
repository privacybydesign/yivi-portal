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
import { Label } from "@/components/ui/label";
import type { UseFormReturn } from "react-hook-form";
import { PhoneInput } from "react-international-phone";
import "react-international-phone/style.css";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const PHONE_INPUT_ID = "organization-contact-number";

// An untouched phone input still holds the dial code of its default country,
// so "is it empty" cannot be answered by comparing against "". No dial code is
// longer than four digits, so anything above that means a number was typed.
const hasPhoneNumber = (value: string | undefined) =>
  (value ?? "").replace(/\D/g, "").length > 4;

export default function ContactField({
  form,
}: {
  form: UseFormReturn<RegistrationInputs>;
}) {
  return (
    <>
      <FormField
        control={form.control}
        name="contact_email"
        rules={{
          required: "An email address is required.",
          pattern: {
            value: EMAIL_PATTERN,
            message: "Enter a valid email address.",
          },
        }}
        render={({ field, fieldState }) => (
          <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
            <div className="py-1">
              <FormLabel>Contact Email</FormLabel>
              <FormDescription>
                Email address of a contact person of this organization. Used
                only for verification purposes and will not be public.
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
        name="contact_number"
        rules={{
          validate: (value) =>
            hasPhoneNumber(value) || "A phone number is required.",
        }}
        render={({ field: { value, onChange, ...field }, fieldState }) => (
          <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
            <div className="py-1">
              {/* PhoneInput takes no id of its own, so FormControl cannot
                  hand it the generated one - label its inner input directly. */}
              <Label htmlFor={PHONE_INPUT_ID}>Contact Number</Label>
              <FormDescription>
                Phone number of a contact person of this organization. Used only
                for verification purposes and will not be public.
              </FormDescription>
            </div>
            <div>
              <div className="border rounded-md shadow-xs">
                <PhoneInput
                  inputProps={{ id: PHONE_INPUT_ID }}
                  defaultCountry="nl"
                  value={value || ""}
                  onChange={onChange}
                  className="flex-1 text-sm outline-none bg-transparent !border-none"
                  inputClassName="!bg-transparent !border-none !border !shadow-none !ring-0 !outline-none w-full"
                  inputStyle={{
                    border: "none",
                    backgroundColor: "transparent",
                  }}
                  {...field}
                />
                <style>{`
                  .react-international-phone-country-selector-button {
                    padding-left: 7px !important;
                  }
                `}</style>
              </div>
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
