import { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { Credential } from "@/models/credential";
import { ChevronDown } from "lucide-react";
import { Environment } from "@/models/yivi-environment";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../../../ui/form";
import type { UseFormReturn } from "react-hook-form";
import type { RelyingPartyFormData } from "../forms/relying-party/validation-schema";
import CredentialSearchFilter from "./attribute-selector/CredentialSearchFilter";
import EnvironmentFilter from "./attribute-selector/EnvironmentFilter";
import AttributeFormField from "./attribute-selector/AttributeFormField";
import ReasonFields from "./attribute-selector/ReasonFields";

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

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-card">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

                        <EnvironmentFilter
                          envFilter={envFilter}
                          toggleEnv={toggleEnv}
                        />

                        <CredentialSearchFilter
                          search={search}
                          credentials={credentials}
                          envFilter={envFilter}
                          setOpen={setOpen}
                          field={field}
                        />
                      </div>
                    </PopoverContent>
                  </Popover>
                </FormControl>
                <FormMessage />
              </FormItem>
            );
          }}
        />

        <AttributeFormField
          index={index}
          credentials={credentials}
          form={form}
        />
      </div>

      <ReasonFields control={form.control} index={index} />
    </div>
  );
}
