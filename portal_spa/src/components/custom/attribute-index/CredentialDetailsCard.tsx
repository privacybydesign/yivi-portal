import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";
import type { Credential } from "@/models/credential";

type Props = {
  credential: Credential;
};
export default function CredentialDetailsCard({ credential }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Credential Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="space-y-3 text-sm">
          <div>
            <dt className="font-medium">Description</dt>
            <dd>{credential.description_en}</dd>
          </div>
          <div>
            <dt className="font-medium">Short Identifier</dt>
            <dd>{credential.credential_id}</dd>
          </div>
          <div>
            <dt className="font-medium">Identifier</dt>
            <dd>{credential.full_path}</dd>
          </div>
          <div>
            <dt className="font-medium">Organization</dt>
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
            <dt className="font-medium">Attestation Provider</dt>
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
          {credential.deprecated_since && (
            <div>
              <dt className="font-medium">Deprecated Since</dt>
              <dd>{credential.deprecated_since}</dd>
            </div>
          )}
          {credential.issue_url && (
            <div>
              <dt className="font-medium">Issue URL</dt>
              <dd className="text-sm">
                <a
                  href={credential.issue_url}
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {credential.issue_url}
                </a>
              </dd>
            </div>
          )}
        </dl>
      </CardContent>
    </Card>
  );
}
