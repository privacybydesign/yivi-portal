import { Checkbox } from "@/components/ui/checkbox";
import { Environment } from "@/models/yivi-environment";

type CredentialSearchFilterProps = {
  envFilter: Record<string, boolean>;
  toggleEnv: (env: Environment) => void;
};
export default function CredentialSearchResult({
  envFilter,
  toggleEnv,
}: CredentialSearchFilterProps) {
  return (
    <div className="w-full overflow-hidden">
      <div className="flex flex-wrap gap-2 text-sm w-full">
        {(Object.values(Environment) as Environment[]).map((env) => (
          <label
            key={env}
            className="flex items-center gap-2 cursor-pointer truncate"
          >
            <Checkbox
              checked={envFilter[env] ?? false}
              onCheckedChange={() => toggleEnv(env)}
            />
            <span className="capitalize text-muted-foreground break-normal">
              {env}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
