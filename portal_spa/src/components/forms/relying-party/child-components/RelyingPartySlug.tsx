import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import type { RelyingPartyFormData } from "../validation-schema";
import type { Control } from "react-hook-form";

type RelyingPartySlugProps = {
  control: Control<RelyingPartyFormData>;
  serverErrors?: Partial<Record<keyof RelyingPartyFormData, string>>;
};

export default function RelyingPartySlug(props: RelyingPartySlugProps) {
  const { control, serverErrors } = props;

  return (
    <div>
      <div className="space-y-2 mt-4">
        <FormField
          control={control}
          name="rp_slug"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Relying party slug
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
                      <Info className="w-3 h-3" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="text-sm">
                      This will serve as a unique identifier for your relying
                      party. Each slug must be distinct — duplicate slugs are
                      not allowed.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage>{serverErrors?.rp_slug}</FormMessage>
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
