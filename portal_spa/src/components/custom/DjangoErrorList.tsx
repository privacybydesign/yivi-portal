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
      {Object.entries(errors).map(([, error], idx) => (
        <li key={idx}>{parseDjangoErrorString(String(error.message))}</li>
      ))}
    </ul>
  );
}
