import {
  FormField,
  FormItem,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { type Control } from "react-hook-form";
import type { RelyingPartyFormData } from "../validation-schema";

export default function AddHostnameFields({
  index,
  control,
  removeHostname,
}: {
  index: number;
  control: Control<RelyingPartyFormData>;
  removeHostname: (index: number) => void;
}) {
  return (
    <FormField
      control={control}
      name={`hostnames.${index}.hostname`}
      render={({ field }) => (
        <FormItem>
          <div className="flex gap-2 items-start">
            <FormControl>
              <Input
                {...field}
                className="w-full"
                placeholder="Enter hostname"
              />
            </FormControl>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => removeHostname(index)}
            >
              Remove
            </Button>
          </div>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
