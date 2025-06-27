import type { FieldErrors } from "react-hook-form";
import type { RelyingPartyFormData } from "../forms/relying-party/validation-schema";
import { parseDjangoErrorString } from "@/actions/manage-relying-party";

export default function DjangoFieldErrors({
  errors,
}: {
  errors: Partial<FieldErrors<RelyingPartyFormData>>;
}) {
  return (
    <ul>
      {Object.entries(errors).map(([, error], idx) => {
        const message =
          typeof error === "object" && error !== null && "message" in error
            ? (error as { message?: string }).message
            : error;
        return <li key={idx}>{parseDjangoErrorString(String(message))}</li>;
      })}
    </ul>
  );
}
