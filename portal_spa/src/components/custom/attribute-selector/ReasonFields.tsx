import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";
import {
  FormField,
  FormLabel,
  FormItem,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import type { Control } from "react-hook-form";

type CredentialSearchResultProps = {
  control: Control<RelyingPartyFormData>;
  index: number;
};
export default function CredentialSearchResult({
  control,
  index,
}: CredentialSearchResultProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <FormField
          control={control}
          name={`attributes.${index}.reason_en`}
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium">
                Reason (English)
              </FormLabel>
              <FormControl>
                <Textarea
                  {...field}
                  placeholder="Enter English reason..."
                  className="min-h-[80px] resize-y"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={control}
          name={`attributes.${index}.reason_nl`}
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium">
                Reason (Dutch)
              </FormLabel>
              <FormControl>
                <Textarea
                  {...field}
                  placeholder="Enter Dutch reason..."
                  className="min-h-[80px] resize-y"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
