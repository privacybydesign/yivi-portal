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
import { LogoPreview } from "@/components/ui/logo-preview";
import { Label } from "@/components/ui/label";
import { UploadIcon } from "lucide-react";
import type { UseFormReturn } from "react-hook-form";
import type { Dispatch, SetStateAction } from "react";

export default function LogoUpload({
  form,
  formState,
  cachedLogo,
  setCachedLogo,
}: {
  form: UseFormReturn<RegistrationInputs>;
  formState: RegistrationFormState;
  cachedLogo?: File | null;
  setCachedLogo: Dispatch<SetStateAction<File | null>>;
}) {
  return (
    <FormField
      control={form.control}
      name="logo"
      render={({ field: { onChange, value, ...field } }) => (
        <FormItem className="grid md:grid-cols-2 items-center md:gap-4">
          <div className="py-1">
            <Label>Organization Logo</Label>
            <FormDescription>Upload your logo (PNG or JPEG).</FormDescription>
          </div>
          <div className="flex flex-col items-start w-full">
            <div className="flex flex-wrap items-center justify-between w-full gap-2">
              <LogoPreview
                control={form.control}
                setValue={form.setValue}
                name={
                  cachedLogo?.name ||
                  (typeof value === "string" ? value : value?.name)
                }
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
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) {
                        setCachedLogo(file);
                      }
                      onChange(file);
                    }}
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
  );
}
