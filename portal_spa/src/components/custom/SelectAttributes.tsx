import { useMemo, useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type { Credential } from "@/models/credential";
import { Check, ChevronDown } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../ui/select";
import { SelectValue } from "@radix-ui/react-select";
import { Environment } from "@/models/yivi-environment";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import type { UseFormReturn } from "react-hook-form";
import type { RelyingPartyFormData } from "../forms/relying-party/validation-schema";

interface CredentialAttributeFieldProps {
  index: number;
  credentials: Array<Credential>;
  form: UseFormReturn<RelyingPartyFormData>;
}

export default function CredentialAttributeFields({
  index,
  credentials,
  form,
}: CredentialAttributeFieldProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [envFilter, setEnvFilter] = useState({
    [Environment.production]: true,
    [Environment.staging]: false,
    [Environment.demo]: false,
  });

  const toggleEnv = (env: Environment) => {
    setEnvFilter((prev) => ({ ...prev, [env]: !prev[env] }));
  };

  const filteredCredentials = useMemo(() => {
    return credentials.filter((cred) => {
      const matchesEnv = envFilter[cred.environment as Environment];

      const inCredentialName =
        cred.name_en.toLowerCase().includes(search.toLowerCase()) ||
        cred.name_nl.toLowerCase().includes(search.toLowerCase());

      const inAttributeName = cred.attributes?.some((attr) =>
        [attr.name_en, attr.name_nl]
          .filter(Boolean)
          .some((name) => name?.toLowerCase().includes(search.toLowerCase()))
      );

      return matchesEnv && (inCredentialName || inAttributeName);
    });
  }, [credentials, envFilter, search]);

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-card">
      {/* Credential and Attribute Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Credential Selection */}
        <FormField
          control={form.control}
          name={`attributes.${index}.credential_id`}
          render={({ field }) => {
            const selected =
              typeof field.value === "number"
                ? credentials.find((cred) => cred.id === field.value)
                : undefined;
            return (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  Credential
                </FormLabel>
                <FormControl>
                  <Popover open={open} onOpenChange={setOpen}>
                    <PopoverTrigger asChild>
                      <div
                        role="combobox"
                        className={cn(
                          "flex h-9 py-2 items-center justify-between rounded-md border border-input bg-transparent px-3 text-sm font-normal shadow-xs hover:bg-accent",
                          !selected && "text-muted-foreground"
                        )}
                        onClick={() => setOpen(!open)}
                      >
                        {selected ? (
                          <span className="truncate">
                            {selected.name_en} ({selected.environment})
                          </span>
                        ) : (
                          <span className="text-muted-foreground">
                            Select credential
                          </span>
                        )}
                        <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </div>
                    </PopoverTrigger>
                    <PopoverContent
                      align="start"
                      sideOffset={0}
                      className="my-1 max-w-none"
                    >
                      <div className="space-y-3">
                        <Input
                          placeholder="Search attributes or credentials"
                          value={search}
                          onChange={(e) => setSearch(e.target.value)}
                          className="h-9"
                        />
                        {/* Environment Filters */}
                        <div className="w-full overflow-hidden">
                          <div className="flex flex-wrap gap-2 text-sm w-full">
                            {(Object.values(Environment) as Environment[]).map(
                              (env) => (
                                <label
                                  key={env}
                                  className="flex items-center gap-2 cursor-pointer truncate"
                                >
                                  <Checkbox
                                    checked={envFilter[env]}
                                    onCheckedChange={() => toggleEnv(env)}
                                  />
                                  <span className="capitalize text-muted-foreground break-normal">
                                    {env}
                                  </span>
                                </label>
                              )
                            )}
                          </div>
                        </div>
                        {/* Credentials List */}
                        <div className="max-h-56 overflow-y-auto border-t pt-2">
                          {filteredCredentials.length === 0 ? (
                            <div className="text-sm text-muted-foreground py-4 text-center">
                              No matching credentials
                            </div>
                          ) : (
                            <div className="space-y-1 w-full overflow-x-hidden">
                              {filteredCredentials.map((cred) => (
                                <button
                                  key={cred.id}
                                  type="button"
                                  className={cn(
                                    "w-full text-left px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors",
                                    cred.id === field.value && "bg-accent"
                                  )}
                                  onClick={() => {
                                    field.onChange(cred.id);
                                    setOpen(false);
                                  }}
                                >
                                  <div className="flex justify-between gap-2 w-full items-start">
                                    <span className="break-words w-full text-left">
                                      {cred.name_en} ({cred.environment})
                                    </span>
                                    {cred.id === field.value && (
                                      <Check className="h-4 w-4 text-primary shrink-0 mt-1" />
                                    )}
                                  </div>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </PopoverContent>
                  </Popover>
                </FormControl>
                <FormMessage />
              </FormItem>
            );
          }}
        />

        {/* Attribute Selection */}
        <FormField
          control={form.control}
          name={`attributes.${index}.credential_attribute_tag`}
          render={({ field }) => {
            const selected =
              typeof form.control._formValues.attributes?.[index]
                ?.credential_id === "number"
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
                            value={attr.name_en}
                          >
                            {attr.name_en}
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
      </div>

      {/* Reason Fields */}
      <div className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name={`attributes.${index}.reason_en`}
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  Reason (English)
                </FormLabel>
                <FormControl>
                  <Textarea
                    {...field}
                    placeholder="Enter English reason..."
                    className="min-h-[80px] resize-y"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name={`attributes.${index}.reason_nl`}
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">
                  Reason (Dutch)
                </FormLabel>
                <FormControl>
                  <Textarea
                    {...field}
                    placeholder="Enter Dutch reason..."
                    className="min-h-[80px] resize-y"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
      </div>
    </div>
  );
}
