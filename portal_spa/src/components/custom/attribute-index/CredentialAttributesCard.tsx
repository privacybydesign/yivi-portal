import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CredentialAttributeDetails } from "./CredentialAttributeDetails";
import { DemoCredentialCard } from "./DemoCredentialCard";
import type { Credential } from "@/models/credential";

type Props = {
  credential: Credential;
};

export default function CredentialAttributesCard({ credential }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Attributes</CardTitle>
      </CardHeader>
      <CardContent>
        {credential.environment === "demo" ? (
          <DemoCredentialCard credential={credential} />
        ) : (
          <div className="space-y-6">
            {credential.attributes.map((attr) => (
              <CredentialAttributeDetails
                key={attr.credential_attribute_tag}
                attr={attr}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
