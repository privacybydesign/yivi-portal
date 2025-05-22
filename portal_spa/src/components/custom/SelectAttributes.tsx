import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "../ui/form";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "../ui/select";
import { Input } from "../ui/input";
import type { Credential } from "@/models/credential";
import { useFormContext } from "react-hook-form";

interface Props {
  index: number;
  credentials: Credential[];
  onRemove: () => void;
}

export default function CredentialAttributeFields({
  index,
  credentials,
}: Props) {
  const form = useFormContext();
  const { control } = form;

  return (
    <div className="border p-4 rounded-md space-y-3">
      <FormField
        control={control}
        name={`attributes.${index}.credential_id`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Credential</FormLabel>
            <Select
              onValueChange={(val) => {
                const intVal = parseInt(val);
                field.onChange(intVal);
                const credential = credentials.find((c) => c.id === intVal);
                const currentAttr = form.getValues(
                  `attributes.${index}.credential_attribute_name`
                );
                if (
                  credential &&
                  !credential.attributes.some((a) => a.name_en === currentAttr)
                ) {
                  form.setValue(
                    `attributes.${index}.credential_attribute_name`,
                    ""
                  );
                }
              }}
              value={field.value?.toString() || ""}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select credential" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {credentials.map((cred) => (
                  <SelectItem key={cred.id} value={String(cred.id)}>
                    {cred.name_en}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name={`attributes.${index}.credential_attribute_name`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Attribute Name</FormLabel>
            <Select onValueChange={field.onChange} value={field.value || ""}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select attribute" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {credentials
                  .find(
                    (c) =>
                      String(c.id) ===
                      form
                        .watch(`attributes.${index}.credential_id`)
                        ?.toString()
                  )
                  ?.attributes.map((attr) => (
                    <SelectItem key={attr.id} value={attr.name_en}>
                      {attr.name_en}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormLabel className="font-medium">Reason</FormLabel>
      <div className="grid md:grid-cols-2 gap-2">
        <FormField
          control={control}
          name={`attributes.${index}.reason_en`}
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm">English</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={control}
          name={`attributes.${index}.reason_nl`}
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm">Dutch</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
