import type {
  RegistrationInputs,
  RegistrationFormState,
} from "@/actions/manage-organization";
import {
  FormField,
  FormItem,
  FormDescription,
  FormMessage,
} from "@/components/ui/form";
import { Label } from "@/components/ui/label";
import type { UseFormReturn } from "react-hook-form";
import { PhoneInput } from "react-international-phone";
import "react-international-phone/style.css";

export default function ContactFields({
  form,
  formState,
}: {
  form: UseFormReturn<RegistrationInputs>;
  formState: RegistrationFormState;
}) {
  return (
    <FormField
      control={form.control}
      name="contact_number"
      render={({ field: { value, onChange, ...field } }) => (
        <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
          <div className="py-1">
            <Label>Contact Number</Label>
            <FormDescription>
              Phone number of a contact person of this organization. Used only
              for verification purposes.
            </FormDescription>
          </div>
          <div>
            <div className="border rounded-md shadow-xs">
              <PhoneInput
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
            {formState.errors.contact_number && (
              <FormMessage className="text-sm text-red-600 mt-1">
                {formState.errors.contact_number.message}
              </FormMessage>
            )}
          </div>
        </FormItem>
      )}
    />
  );
}
