import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import type { RelyingPartyFormData } from "../validation-schema";
import type { Control } from "react-hook-form";
import { Link } from "react-router-dom";

type ContextDescriptionProps = {
  control: Control<RelyingPartyFormData>;
};

export default function ContextDescription({
  control,
}: ContextDescriptionProps) {
  return (
    <div className="space-y-2 mt-4">
      <FormLabel className="text-base font-medium">
        Context description
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
              <Info className="w-3 h-3" />
            </div>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p className="text-sm text-justify">
              Provide a short description of the context in which you're using
              Yivi and the selected attributes. For example: "Access to employee
              portal" or "Proof of age for alcohol purchase". Read more about
              why we ask for this information{" "}
              <Link
                to="/faq#why-context-description"
                className="text-blue-600 hover:underline"
              >
                here
              </Link>
              .
            </p>
          </TooltipContent>
        </Tooltip>
      </FormLabel>

      <FormField
        control={control}
        name="context_description_en"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm">English</FormLabel>
            <FormControl>
              <Textarea {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="context_description_nl"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm">Dutch</FormLabel>
            <FormControl>
              <Textarea {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormMessage />
    </div>
  );
}
