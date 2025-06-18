import { FormLabel } from "@/components/ui/form";
import AddHostnameFields from "./AddHostnameFields";
import { Button } from "@/components/ui/button";
import type {
  FieldArrayWithId,
  FieldErrors,
  UseFormRegister,
} from "react-hook-form";
import type { RelyingPartyFormData } from "../validation-schema";

type HostnameProps = {
  hostnameFields: FieldArrayWithId<RelyingPartyFormData, "hostnames">[];
  register: UseFormRegister<RelyingPartyFormData>;
  removeHostname: (index: number) => void;
  appendHostname: (data: { hostname: string }) => void;
  errors: FieldErrors<RelyingPartyFormData>;
};
export default function Hostnames(props: HostnameProps) {
  const { hostnameFields, register, removeHostname, appendHostname, errors } =
    props;

  return (
    <div className="space-y-2 mt-4">
      <FormLabel className="font-medium">Hostnames</FormLabel>

      <div className="space-y-2 rounded-md">
        {hostnameFields.map((field, index) => (
          <AddHostnameFields
            key={field.id || index}
            field={field}
            index={index}
            register={register}
            removeHostname={removeHostname}
            errors={errors}
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
