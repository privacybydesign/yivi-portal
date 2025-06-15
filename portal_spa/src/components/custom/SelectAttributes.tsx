import { useMemo, useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type { Credential } from "@/models/credential";
import { Check, ChevronDown } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../ui/select";
import { SelectValue } from "@radix-ui/react-select";

interface CredentialAttributeFieldProps {
  index: number;
  credentials: Credential[];
  value: {
    credential_id: number;
    credential_attribute_name: string;
    reason_en: string;
    reason_nl: string;
  };
  onChange: (updated: {
    credential_id: number;
    credential_attribute_name: string;
    reason_en: string;
    reason_nl: string;
  }) => void;
}

export default function CredentialAttributeFields({
  credentials,
  value,
  onChange,
}: CredentialAttributeFieldProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [envFilter, setEnvFilter] = useState({
    production: true,
    staging: false,
    demo: false,
  });

  const toggleEnv = (env: keyof typeof envFilter) => {
    setEnvFilter((prev) => ({ ...prev, [env]: !prev[env] }));
  };

  const filteredCredentials = useMemo(() => {
    return credentials.filter((cred) => {
      const matchesEnv = envFilter[cred.environment as keyof typeof envFilter];

      const inCredentialName =
        cred.name_en.toLowerCase().includes(search.toLowerCase()) ||
        cred.name_nl.toLowerCase().includes(search.toLowerCase());

      const inAttributeName = cred.attributes?.some((attr) =>
        [attr.name_en, attr.name_nl]
          .filter(Boolean)
          .some((name) => name.toLowerCase().includes(search.toLowerCase()))
      );

      return matchesEnv && (inCredentialName || inAttributeName);
    });
  }, [credentials, envFilter, search]);

  const selected = credentials.find((cred) => cred.id === value?.credential_id);

  const handleFieldChange = (fieldKey: string, newValue: unknown) => {
    onChange?.({
      ...value,
      [fieldKey]: newValue,
    });
  };

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-card">
      {/* Credential and Attribute Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Credential Selection */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Credential</Label>
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
                    {(["production", "staging", "demo"] as const).map((env) => (
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
                    ))}
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
                            cred.id === value?.credential_id && "bg-accent"
                          )}
                          onClick={() => {
                            handleFieldChange("credential_id", cred.id);
                            setOpen(false);
                          }}
                        >
                          <div className="flex justify-between gap-2 w-full items-start">
                            <span className="break-words w-full text-left">
                              {cred.name_en} ({cred.environment})
                            </span>
                            {cred.id === value?.credential_id && (
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
        </div>

        {/* Attribute Selection */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Attribute</Label>
          {selected && selected.attributes?.length > 0 ? (
            <Select
              value={value?.credential_attribute_name ?? ""}
              onValueChange={(val) =>
                handleFieldChange("credential_attribute_name", val)
              }
            >
              <SelectTrigger className="flex w-full items-center justify-between rounded-md border bg-transparent px-3 text-sm font-normal hover:bg-accent">
                <SelectValue placeholder="Select attribute" />
              </SelectTrigger>
              <SelectContent>
                {selected.attributes.map((attr) => (
                  <SelectItem
                    key={attr.credential_attribute_id}
                    value={`${attr.name_en}`}
                  >
                    {attr.name_en}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <div className="relative">
              <Input
                disabled
                placeholder="Select a credential first"
                value=""
                className="h-9 px-3 text-sm font-normal"
              />
            </div>
          )}
        </div>
      </div>

      {/* Reason Fields */}
      <div className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-sm font-medium">Reason (English)</Label>
            <Textarea
              value={value?.reason_en ?? ""}
              onChange={(e) => handleFieldChange("reason_en", e.target.value)}
              placeholder="Enter English reason..."
              className="min-h-[80px] resize-y"
            />
          </div>
          <div className="space-y-2">
            <Label className="text-sm font-medium">Reason (Dutch)</Label>
            <Textarea
              value={value?.reason_nl ?? ""}
              onChange={(e) => handleFieldChange("reason_nl", e.target.value)}
              placeholder="Enter Dutch reason..."
              className="min-h-[80px] resize-y"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
