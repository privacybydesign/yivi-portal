import type { Control, UseFormSetValue } from "react-hook-form";
import { useWatch } from "react-hook-form";
import { useEffect, useMemo } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { RegistrationInputs } from "@/actions/manage-organization";
import { apiEndpoint } from "@/services/axiosInstance";

export function LogoPreview({
  control,
  name,
}: {
  control: Control<RegistrationInputs>;
  setValue: UseFormSetValue<RegistrationInputs>;
  name: string | undefined;
}) {
  const logo = useWatch({ control, name: "logo" });

  // A picked file needs an object URL, released again when it changes or the
  // preview unmounts; a stored logo is a path on the API.
  const fileURL = useMemo(
    () => (logo instanceof File ? URL.createObjectURL(logo) : null),
    [logo],
  );
  useEffect(
    () => () => {
      if (fileURL) URL.revokeObjectURL(fileURL);
    },
    [fileURL],
  );

  const logoURL =
    typeof logo === "string"
      ? apiEndpoint + logo
      : (fileURL ?? "/logo-placeholder.svg");

  return (
    <div className="relative size-24">
      <Avatar className="!size-24">
        <AvatarImage
          src={logoURL}
          className="rounded-full border object-contain"
        />
        <AvatarFallback>{name}</AvatarFallback>
      </Avatar>
    </div>
  );
}
