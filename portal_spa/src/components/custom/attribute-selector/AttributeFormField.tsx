import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import type { UseFormReturn } from "react-hook-form";
import type { Credential } from "@/models/credential";
import { getLocalizedField } from "@/utils/getLocalizedField";
import i18n from "@/i18n";

type AttributeFormFieldProps = {
  index: number;
  credentials: Array<Credential>;
  form: UseFormReturn<RelyingPartyFormData>;
};

export default function AttributeFormField({
  index,
  credentials,
  form,
}: AttributeFormFieldProps) {
  return (
    <FormField
      control={form.control}
      name={`attributes.${index}.credential_attribute_tag`}
      render={({ field }) => {
        const selected =
          typeof form.control._formValues.attributes?.[index]?.credential_id ===
          "number"
            ? credentials.find(
                (cred) =>
                  cred.id ===
                  form.control._formValues.attributes[index]?.credential_id
              )
            : undefined;
        return (
          <FormItem>
            <FormLabel className="text-sm font-medium">Attribute</FormLabel>
            <FormControl>
              {selected && selected.attributes?.length > 0 ? (
                <Select
                  value={field.value ?? ""}
                  onValueChange={field.onChange}
                >
                  <SelectTrigger className="flex w-full items-center justify-between rounded-md border bg-transparent px-3 text-sm font-normal hover:bg-accent">
                    <SelectValue placeholder="Select attribute" />
                  </SelectTrigger>
                  <SelectContent>
                    {selected.attributes.map((attr) => (
                      <SelectItem
                        key={attr.credential_attribute_tag}
                        value={getLocalizedField(attr, "name", i18n.language)}
                      >
                        {getLocalizedField(attr, "name", i18n.language)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Input
                  disabled
                  placeholder="Select a credential first"
                  className="h-9 px-3 text-sm font-normal"
                />
              )}
            </FormControl>
            <FormMessage />
          </FormItem>
        );
      }}
    />
  );
}
