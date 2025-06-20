import type {
  RegistrationFormState,
  RegistrationInputs,
} from "@/actions/manage-organization";
import { CountryDropdown } from "@/components/ui/country-dropdown";
import {
  FormField,
  FormItem,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { UseFormReturn } from "react-hook-form";

export default function ContactAddressBox({
  form,
  formState,
}: {
  form: UseFormReturn<RegistrationInputs>;
  formState: RegistrationFormState;
}) {
  return (
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
                  {formState.errors.street.message}
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
                  {formState.errors.house_number.message}
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
                  {formState.errors.postal_code.message}
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
                  {formState.errors.city.message}
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
                <>
                  <Input type="hidden" {...field} />

                  <CountryDropdown
                    placeholder="Country"
                    defaultValue={field.value}
                    onChange={(country) => {
                      field.onChange(country.alpha2);
                      form.setValue("country", country.alpha2);
                    }}
                  />
                </>
              </FormControl>

              {formState.errors.country && (
                <FormMessage className="text-sm text-red-600 mt-1">
                  {formState.errors.country.message}
                </FormMessage>
              )}
            </div>
          </FormItem>
        )}
      />
    </fieldset>
  );
}
