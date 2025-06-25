import { cn } from "@/lib/utils";
import type { Environment } from "@/models/yivi-environment";
import { Check } from "lucide-react";
import { useMemo } from "react";
import type { ControllerRenderProps } from "react-hook-form";
import type { Credential } from "@/models/credential";
import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";

type CredentialSearchFilterProps = {
  search: string;
  credentials: Credential[];
  envFilter: Record<string, boolean>;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  field: ControllerRenderProps<RelyingPartyFormData>;
};
export default function CredentialSearchFilter({
  search,
  credentials,
  envFilter,
  setOpen,
  field,
}: CredentialSearchFilterProps) {
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
  );
}
