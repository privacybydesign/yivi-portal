/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { axiosInstance } from "@/services/axiosInstance";
import { CredentialAttributeDetails } from "./CredentialAttributeDetails";
import type { Credential } from "@/models/credential";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";

type Props = {
  credential: Credential;
};

export function DemoCredentialCard({ credential }: Props) {
  const [attributeValues, setAttributeValues] = useState<{
    [key: string]: string;
  }>({});
  const [loading, setLoading] = useState(false);
  const { i18n } = useTranslation();

  const handleChange = (id: string, value: string) => {
    setAttributeValues((prev) => ({ ...prev, [id]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const missing = credential.attributes.find(
      (attr) => !attributeValues[attr.credential_attribute_tag]?.trim()
    );
    if (missing) {
      toast.error(`Please fill in: ${missing.name_en}`);
      return;
    }
    try {
      setLoading(true);
      const yivi: any = await import("@privacybydesign/yivi-frontend");
      const popup = yivi.newPopup({
        debugging: import.meta.env.DEV,
        language: i18n.language,
        translations: {
          header:
            'Issuing demo credential with <i class="yivi-web-logo">Yivi</i>',
        },
        session: {
          url: axiosInstance.defaults.baseURL + "/v1",
          start: {
            url: (o: any) => `${o.url}/demo-issuance`,
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              credential: credential.full_path,
              attributes: attributeValues,
            }),
          },
          result: {
            url: (o: any, { sessionToken }: any) =>
              `${o.url}/demo-issuance/token/${sessionToken}`,
            method: "GET",
            credentials: "include",
          },
        },
      });
      await popup.start({});
      toast.success("Demo credential issued successfully.");
    } catch (e) {
      toast.error(`Failed to issue demo credential. error: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {credential.attributes.map((attr) => (
        <CredentialAttributeDetails
          key={attr.credential_attribute_tag}
          attr={attr}
          value={attributeValues[attr.credential_attribute_tag] || ""}
          onChange={(val) => handleChange(attr.credential_attribute_tag, val)}
          environment="demo"
        />
      ))}
      <Button type="submit" disabled={loading}>
        {loading ? "Issuing..." : "Issue Demo Credential"}
      </Button>
    </form>
  );
}
