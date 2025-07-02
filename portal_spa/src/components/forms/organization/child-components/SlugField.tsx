import type {
  RegistrationInputs,
  RegistrationFormState,
} from "@/actions/manage-organization";
import {
  FormField,
  FormItem,
  FormDescription,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { generateSlug } from "@/lib/utils";
import { Label } from "@/components/ui/label";
import type { UseFormReturn } from "react-hook-form";

export default function SlugField({
  form,
  formState,
}: {
  form: UseFormReturn<RegistrationInputs>;
  formState: RegistrationFormState;
}) {
  return (
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
                pattern="[a-zA-Z0-9\-]+"
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
  );
}
