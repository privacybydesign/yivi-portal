import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AttestationProvider } from "@/models/attestationprovider";
import { axiosInstance } from "@/services/axiosInstance";
import { toast } from "sonner";
import { apiEndpoint } from "@/services/axiosInstance";
import { Badge } from "@/components/ui/badge";

export default function AttestationProviderDetailsPage() {
  const { org_slug, environment, ap_slug } = useParams();
  const [apDetails, setApDetails] = useState<AttestationProvider | null>(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });

    if (!org_slug || !environment || !ap_slug) return;

    const fetchAttestationProviderDetails = async () => {
      try {
        const response = await axiosInstance.get(
          `/v1/yivi/organizations/${org_slug}/attestation-provider/${environment}/${ap_slug}/`,
        );
        setApDetails(response.data);
      } catch (error) {
        toast.error(
          `Failed to fetch details for ${ap_slug}: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    };

    fetchAttestationProviderDetails();
  }, [org_slug, environment, ap_slug]);

  return (
    <div className="space-y-8">
      <div className="mb-4">
        {apDetails?.organization_logo && (
          <img
            src={`${apiEndpoint}${apDetails.organization_logo}`}
            width={15}
            height={15}
            alt={`${apDetails.organization} logo`}
            className="h-15 w-15 mb-2 rounded shadow border object-contain"
          />
        )}
      </div>
      <h1 className="text-3xl font-semibold flex items-center gap-3">
        {apDetails?.organization}
        {apDetails?.deprecated_since && (
          <Badge variant="destructive">Deprecated</Badge>
        )}
      </h1>

      {/* Provider Details Card */}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            Attestation Provider Details
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-3">
          <>
            <div>
              <span className="font-medium">Identifier:</span>{" "}
              {apDetails?.ap_slug}
            </div>
            {apDetails?.full_path && (
              <div>
                <span className="font-medium">Full Identifier:</span>{" "}
                {apDetails.full_path}
              </div>
            )}
            <div>
              <span className="font-medium">Organization:</span>{" "}
              <Link to={`/organizations/${org_slug}`} className="text-blue-600">
                {apDetails?.organization}
              </Link>
            </div>
            <div>
              <span className="font-medium">Environment:</span>{" "}
              <Link
                to={`/attribute-index/environments/${environment}/`}
                className="text-blue-600"
              >
                {environment}
              </Link>
            </div>
            {apDetails?.contact_email && (
              <div>
                <span className="font-medium">Contact Email:</span>{" "}
                <a
                  href={`mailto:${apDetails.contact_email}`}
                  className="text-blue-600 hover:underline"
                >
                  {apDetails.contact_email}
                </a>
              </div>
            )}

            {apDetails?.contact_address && (
              <div>
                <span className="font-medium">Contact Website:</span>{" "}
                <a
                  href={apDetails.contact_address}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {apDetails.contact_address}
                </a>
              </div>
            )}
          </>
        </CardContent>
      </Card>

      {/* Credentials Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            Credentials Issued by this Provider
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          {apDetails?.credentials?.length ? (
            apDetails.credentials.map((cred) => (
              <div key={cred.id} className="border p-4 rounded">
                <h3 className="font-semibold">
                  <Link
                    to={`/attribute-index/credentials/${environment}/${ap_slug}/${cred.credential_id}`}
                    className="text-blue-600 hover:underline"
                  >
                    {cred.name_en} ({cred.credential_id})
                  </Link>
                </h3>
                <p className="text-muted-foreground">{cred.description_en}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-500">
              No credentials found for this provider.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
