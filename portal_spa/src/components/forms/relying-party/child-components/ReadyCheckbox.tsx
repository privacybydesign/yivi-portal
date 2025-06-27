import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import type { Control } from "react-hook-form";
import type { RelyingPartyFormData } from "../validation-schema";

type ReadyCheckboxProps = {
  control: Control<RelyingPartyFormData>;
};

export default function ReadyCheckbox(props: ReadyCheckboxProps) {
  const { control } = props;

  return (
    <div className="space-y-2 mt-4">
      <FormField
        control={control}
        name="ready"
        render={({ field }) => (
          <FormItem className="flex items-center space-x-3 space-y-0">
            <FormControl>
              <Checkbox
                checked={field.value}
                onCheckedChange={field.onChange}
                id="ready-checkbox"
              />
            </FormControl>
            <FormLabel
              htmlFor="ready-checkbox"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
            >
              Mark as ready
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
                    <Info className="w-3 h-3" />
                  </div>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-md break-words">
                  <p className="justify-center text-sm">
                    Marking this relying party as "ready" indicates that it is
                    prepared for review and publication. You may choose to leave
                    it unmarked — in that case, your registration will remain in
                    draft form and will not be finalized.
                  </p>
                </TooltipContent>
              </Tooltip>
            </FormLabel>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
