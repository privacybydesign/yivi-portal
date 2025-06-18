import { Input } from "@/components/ui/input";
import type { CredentialAttribute } from "@/models/credential";

type Props = {
  attr: CredentialAttribute;
  value?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
};

export function CredentialAttributeDetails({ attr, value, onChange }: Props) {
  return (
    <div className="border text-sm rounded-lg overflow-hidden">
      <div className="overflow-x-auto p-4 space-y-1">
        <div className="w-max">
          <span className="font-mono font-bold">{attr.name_en}</span>
          <span className="italic"> ({attr.credential_attribute_id})</span>
        </div>
        <div className="w-max">
          <span className="font-medium">Identifier:</span>{" "}
          <span className="font-mono">{attr.full_path}</span>
        </div>
        <div className="w-max">
          <span className="font-medium">Description:</span>{" "}
          {attr.description_en}
        </div>
        <div className="w-max pt-3">
          <Input
            id={`attribute-${attr.credential_attribute_id}`}
            placeholder={attr.name_en}
            value={value || ""}
            onChange={(e) => onChange?.(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
