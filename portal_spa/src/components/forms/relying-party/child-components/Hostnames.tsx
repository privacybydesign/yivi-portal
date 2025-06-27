import { FormLabel } from "@/components/ui/form";
import AddHostnameFields from "./AddHostnameFields";
import { Button } from "@/components/ui/button";
import { type Control, useFieldArray } from "react-hook-form";
import type { RelyingPartyFormData } from "../validation-schema";

type HostnameProps = {
  control: Control<RelyingPartyFormData>;
};

export default function Hostnames(props: HostnameProps) {
  const { control } = props;
  const {
    fields: hostnameFields,
    append: appendHostname,
    remove: removeHostname,
  } = useFieldArray({
    control,
    name: "hostnames",
  });
  return (
    <div className="space-y-2 mt-4">
      <FormLabel className="font-medium">Hostnames</FormLabel>

      <div className="space-y-2 rounded-md">
        {hostnameFields.map((field, index) => (
          <AddHostnameFields
            key={field.id || index}
            control={control}
            index={index}
            removeHostname={removeHostname}
          />
        ))}
      </div>

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => appendHostname({ hostname: "" })}
      >
        Add hostname
      </Button>
    </div>
  );
}
