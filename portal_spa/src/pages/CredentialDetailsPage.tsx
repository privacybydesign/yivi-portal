import { useOutletContext, useParams } from "react-router-dom";
import type { Credential } from "@/models/credential";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useEffect } from "react";
import { Info } from "lucide-react";
import CredentialDetailsCard from "@/components/custom/attribute-index/CredentialDetailsCard";
import CredentialAttributesCard from "@/components/custom/attribute-index/CredentialAttributesCard";

type OutletContext = {
  credentials: Credential[];
};

export default function CredentialDetailsPage() {
  const { credentials } = useOutletContext<OutletContext>();
  const { environment, ap_slug, credential_id } = useParams();

  const credential = credentials.find(
    (c) =>
      c.environment === environment &&
      c.ap_slug === ap_slug &&
      c.credential_id === credential_id
  );

  useEffect(
    () => window.scrollTo({ top: 0, behavior: "smooth" }),
    [credential]
  );

  if (!credentials?.length) {
    return (
      <>
        <Skeleton className="h-9 w-3/5"></Skeleton>
        <Skeleton className="mt-8 h-screen w-full"></Skeleton>
      </>
    );
  }

  if (!credential) {
    return <div className="text-sm text-red-500">Credential not found.</div>;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <h1 className="text-3xl font-semibold flex items-center gap-x-3">
        {credential.name_en}
        {credential.deprecated_since && (
          <Badge variant="destructive">Deprecated</Badge>
        )}
      </h1>

      {/* Demo info */}
      {credential.environment === "demo" && (
        <div className="flex items-center gap-x-2 rounded-md bg-yellow-50 p-4 text-yellow-800">
          <Info className="h-8 w-8 mr-3" />
          <span>
            You can obtain this credential by filling out the attribute fields
            below. This demo credential has no real value, other than to
            demonstrate the experience of a Yivi credential issuance.
          </span>
        </div>
      )}

      {/* Credential Details */}
      <CredentialDetailsCard credential={credential} />


      {/* Attributes */}
      <CredentialAttributesCard credential={credential} />
    </div>
  );
}
