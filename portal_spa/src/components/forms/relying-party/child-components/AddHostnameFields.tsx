import { Button } from "@/components/ui/button";
import { FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import type {
  FieldArrayWithId,
  FieldErrors,
  UseFormRegister,
} from "react-hook-form";
import type { RelyingPartyFormData } from "../validation-schema";

type AddHostnameFieldsProps = {
  field: FieldArrayWithId<RelyingPartyFormData, "hostnames">;
  index: number;
  register: UseFormRegister<RelyingPartyFormData>;
  removeHostname: (index: number) => void;
  errors: FieldErrors<RelyingPartyFormData>;
};
export default function AddHostnameFields(props: AddHostnameFieldsProps) {
  const { field, index, register, removeHostname, errors } = props;
  return (
    <>
      <div key={index} className="flex gap-2 items-start">
        {typeof field.id === "number" && (
          <Input
            type="hidden"
            {...register(`hostnames.${index}.id`, {
              valueAsNumber: true,
            })}
            defaultValue={field.id}
          />
        )}

        <Input
          {...register(`hostnames.${index}.hostname`)}
          defaultValue={field.hostname}
          className="w-full"
        />
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => removeHostname(index)}
        >
          Remove
        </Button>
        <FormMessage>
          {errors.hostnames?.[index]?.hostname?.message}
        </FormMessage>
      </div>
    </>
  );
}
