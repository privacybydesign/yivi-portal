import CredentialAttributeFields from "@/components/custom/SelectAttributes";
import { Button } from "@/components/ui/button";
import { FormLabel } from "@/components/ui/form";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import type { Credential, CredentialAttribute } from "@/models/credential";
import type { RelyingPartyFormData } from "../validation-schema";
import type { FieldArrayWithId, UseFormReturn } from "react-hook-form";

type CredentialAttributeProps = {
  attrFields: FieldArrayWithId<RelyingPartyFormData, "attributes">[];
  form: UseFormReturn<RelyingPartyFormData>;
  credentials: Array<Credential>;
  appendAttr: (attr: CredentialAttribute) => void;
  removeAttr: (index: number) => void;
};

export function CredentialAttributes(props: CredentialAttributeProps) {
  const { attrFields, form, credentials, appendAttr, removeAttr } = props;
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
            <p className="text-sm">
              In this section, specify the Yivi credential attributes you intend
              to request from users through this relying party.
            </p>
          </TooltipContent>
        </Tooltip>
      </FormLabel>
      <div className="space-y-2">
        {attrFields.map((field, index) => (
          <div key={field.id} className="rounded-md space-y-3">
            <CredentialAttributeFields
              index={index}
              credentials={credentials}
              value={{
                ...form.getValues(`attributes.${index}`),
              }}
              onChange={(updatedAttr) =>
                form.setValue(`attributes.${index}`, updatedAttr, {
                  shouldValidate: true,
                })
              }
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
              credential_attribute_id: "",
              reason_en: "",
              reason_nl: "",
              credential_id: -1, // won't match to any credential
            })
          }
        >
          Add attribute
        </Button>
      </div>
    </div>
  );
}
