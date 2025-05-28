import { Link, useOutletContext, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Credential } from "@/models/credential";

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

  if (!credential) {
    return (
      <div className="p-4 text-sm text-red-500">Credential not found.</div>
    );
  }

  return (
    <div className="space-y-8 p-4">
      <h1 className="text-3xl font-semibold">
        {credential.name_en} Credential
      </h1>

      {/* Credential Details */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Credential Details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="font-medium">Short Identifier</dt>
              <dd>{credential.credential_id}</dd>
            </div>
            <div>
              <dt className="font-medium">Identifier</dt>
              <dd>{credential.full_path}</dd>
            </div>
            <div>
              <dt className="font-medium">Issued by</dt>
              <dd>
                <Link
                  to={`/organizations/${credential.org_slug}`}
                  className="text-blue-600"
                >
                  {credential.org_name}
                </Link>
              </dd>
            </div>
            <div>
              <dt className="font-medium">Attestation provider</dt>
              <dd>
                <Link
                  to={`/attribute-index/attestation-provider/${credential.org_slug}/${credential.environment}/${credential.ap_slug}`}
                  className="text-blue-600"
                >
                  {credential.ap_slug}
                </Link>
              </dd>
            </div>
            <div>
              <dt className="font-medium">Environment</dt>
              <dd>
                <Link
                  to={`/attribute-index/environments/${credential.environment}`}
                  className="text-blue-600"
                >
                  {credential.environment}
                </Link>
              </dd>
            </div>
            <div>
              <dt className="font-medium">Description</dt>
              <dd>{credential.description_en}</dd>
            </div>
            <div>
              <dt className="font-medium">Issue URL</dt>
              <dd>
                <a href={credential.issue_url} className="text-blue-600">
                  {credential.issue_url}
                </a>
              </dd>
            </div>
          </dl>
        </CardContent>

        {/* Attributes */}
        <CardHeader>
          <CardTitle className="text-lg">Attributes</CardTitle>
        </CardHeader>
        <CardContent>
          {credential.attributes.length === 0 ? (
            <p className="text-sm text-gray-500">
              No attributes defined for this credential.
            </p>
          ) : (
            <div className="space-y-6">
              {credential.attributes.map((attr) => (
                <div
                  className="border p-4 rounded-lg"
                  key={attr.credential_attribute_id}
                >
                  <div key={attr.id} className="text-sm space-y-1">
                    <div>
                      <span className="font-mono font-bold">
                        {attr.name_en}
                      </span>
                      <span className="italic">
                        {" "}
                        ({attr.credential_attribute_id})
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Identifier:</span>{" "}
                      <span className="font-mono">{attr.full_path}</span>
                    </div>
                    <div>
                      <span className="font-medium">Description:</span>{" "}
                      {attr.description_en}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
