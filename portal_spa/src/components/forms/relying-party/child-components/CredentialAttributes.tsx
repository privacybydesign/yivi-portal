import CredentialAttributeFields from "@/components/forms/relying-party/child-components/SelectAttributes";
import { Button } from "@/components/ui/button";
import { FormLabel } from "@/components/ui/form";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import type { Credential } from "@/models/credential";
import type { RelyingPartyFormData } from "../validation-schema";
import { useFieldArray, type UseFormReturn } from "react-hook-form";
import { Link } from "react-router-dom";

type CredentialAttributeProps = {
  form: UseFormReturn<RelyingPartyFormData>;
  credentials: Array<Credential>;
};

export function CredentialAttributes(props: CredentialAttributeProps) {
  const { form, credentials } = props;

  const {
    fields: attrFields,
    append: appendAttr,
    remove: removeAttr,
  } = useFieldArray({ control: form.control, name: "attributes" });

  return (
    <div className="space-y-2 mt-4">
      <FormLabel className="text-base font-medium">
        Credential attributes
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
              <Info className="w-3 h-3" />
            </div>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p className="text-sm max-w-3xs">
              In this section, specify the Yivi credential attributes you intend
              to request from users through this relying party. Read more about
              why we ask for this information{" "}
              <Link
                to="/faq#why-select-attributes-for-relying-party"
                className="text-blue-600 hover:underline"
              >
                here
              </Link>
            </p>
          </TooltipContent>
        </Tooltip>
      </FormLabel>
      <div className="space-y-2">
        {attrFields.map((field, index) => (
          <div key={field.id} className="rounded-md space-y-3">
            <CredentialAttributeFields
              form={form}
              index={index}
              credentials={credentials}
            />

            <div className="flex justify-end">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeAttr(index)}
              >
                Remove attribute
              </Button>
            </div>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() =>
            appendAttr({
              credential_id: -1,
              credential_attribute_tag: "",
              reason_en: "",
              reason_nl: "",
            })
          }
        >
          Add attribute
        </Button>
        {form.formState?.errors.attributes && (
          <p className="text-sm text-red-500">
            {form.formState?.errors.attributes?.message}
          </p>
        )}
      </div>
    </div>
  );
}
