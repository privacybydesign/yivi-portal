import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { generateSlug } from "@/lib/utils";
import { Label } from "@/components/ui/label";
import type { UseFormReturn } from "react-hook-form";
import type {
  RegistrationFormState,
  RegistrationInputs,
} from "@/actions/manage-organization";

export default function OrganizationNameFields({
  form,
  formState,
}: {
  form: UseFormReturn<RegistrationInputs>;
  formState: RegistrationFormState;
}) {
  return (
    <div>
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
                  {formState.errors.name_nl.message}
                </FormMessage>
              )}
            </div>
          </FormItem>
        )}
      />
    </div>
  );
}
