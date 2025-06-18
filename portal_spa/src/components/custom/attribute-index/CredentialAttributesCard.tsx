import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CredentialAttributeDetails } from "./CredentialAttributeDetails";
import { DemoCredentialForm } from "./DemoCredentialCard";
import type { Credential } from "@/models/credential";

type Props = {
  credential: Credential;
};

export default function CredentialDetailsCard({ credential }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Attributes</CardTitle>
      </CardHeader>
      <CardContent>
        {credential.attributes.length === 0 ? (
          <p className="text-sm text-gray-500">
            No attributes defined for this credential.
          </p>
        ) : credential.environment === "demo" ? (
          <DemoCredentialForm credential={credential} />
        ) : (
          <div className="space-y-6">
            {credential.attributes.map((attr) => (
              <CredentialAttributeDetails
                key={attr.credential_attribute_id}
                attr={attr}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
