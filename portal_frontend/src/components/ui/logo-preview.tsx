"use client";

import { Control, UseFormSetValue, useWatch } from "react-hook-form";
import { useEffect, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/src/components/ui/avatar";
import { XIcon } from "lucide-react";
import getConfig from 'next/config';
import { RegistrationInputs } from "@/src/actions/manage-organization";

export function LogoPreview({
  control,
  setValue,
  name,
}: {
  control: Control<RegistrationInputs>;
  setValue: UseFormSetValue<RegistrationInputs>;
  name: string | undefined;
}) {
  const { publicRuntimeConfig } = getConfig();
  const logo = useWatch({ control, name: "logo" });

  const [logoURL, setLogoURL] = useState<string>('/logo-placeholder.svg');

  useEffect(() => {
    if (typeof logo === "string") {
      setLogoURL(publicRuntimeConfig.API_ENDPOINT + logo);
    } else if (logo instanceof File) {
      const objectUrl = URL.createObjectURL(logo);
      setLogoURL(objectUrl);

      // Clean up object URL on unmount or when file changes
      return () => {
        URL.revokeObjectURL(objectUrl);
      };
    } else {
      setLogoURL('/logo-placeholder.svg');
    }
  }, [logo, publicRuntimeConfig.API_ENDPOINT]);

  const clearLogo = () => {
    setValue("logo", undefined);
    setLogoURL('/logo-placeholder.svg');
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