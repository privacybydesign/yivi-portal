import type { Control, UseFormSetValue } from "react-hook-form";
import { useWatch } from "react-hook-form";
import { useEffect, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { XIcon } from "lucide-react";
import type { RegistrationInputs } from "@/actions/manage-organization";
import { apiEndpoint } from "@/services/axiosInstance";

export function LogoPreview({
  control,
  setValue,
  name,
}: {
  control: Control<RegistrationInputs>;
  setValue: UseFormSetValue<RegistrationInputs>;
  name: string | undefined;
  onClear?: () => void;
}) {
  const logo = useWatch({ control, name: "logo" });

  const [logoURL, setLogoURL] = useState<string>("/logo-placeholder.svg");

  useEffect(() => {
    if (typeof logo === "string") {
      setLogoURL(apiEndpoint + logo);
    } else if (logo instanceof File) {
      const objectUrl = URL.createObjectURL(logo);
      setLogoURL(objectUrl);

      // Clean up object URL on unmount or when file changes
      return () => {
        URL.revokeObjectURL(objectUrl);
      };
    } else {
      setLogoURL("/logo-placeholder.svg");
    }
  }, [logo, apiEndpoint]);

  const clearLogo = () => {
    setValue("logo", undefined, { shouldDirty: true });
    setLogoURL("/logo-placeholder.svg");
  };

  return (
    <div className="relative size-24">
      <Avatar className="!size-24">
        <AvatarImage
          src={logoURL}
          className="rounded-full border object-contain"
        />
        <AvatarFallback>{name}</AvatarFallback>
      </Avatar>

      {logo && (
        <button
          type="button"
          onClick={clearLogo}
          className="bg-red-400 rounded-full p-1 absolute top-0 right-0"
        >
          <XIcon size={12} strokeWidth={3} />
        </button>
      )}
    </div>
  );
}
