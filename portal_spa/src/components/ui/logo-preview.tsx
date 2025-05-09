import type { Control, UseFormSetValue } from "react-hook-form";
import { useWatch } from "react-hook-form";
import { useEffect, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { XIcon } from "lucide-react";
import type { RegistrationInputs } from "@/actions/manage-organization";

export function LogoPreview({
  control,
  setValue,
  name,
}: {
  control: Control<RegistrationInputs>;
  setValue: UseFormSetValue<RegistrationInputs>;
  name: string | undefined;
}) {
  const logo = useWatch({ control, name: "logo" });

  const [logoURL, setLogoURL] = useState<string>("/logo-placeholder.svg");
  const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

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
    setValue("logo", undefined);
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
