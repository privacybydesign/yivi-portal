/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { axiosInstance } from "@/services/axiosInstance";
import { CredentialAttributeDetails } from "./CredentialAttributeDetails";
import type { Credential } from "@/models/credential";
import { toast } from "sonner";

type Props = {
  credential: Credential;
};

const buildDemoValues = (credential: Credential) =>
  Object.fromEntries(
    credential.attributes
      .filter((attr) => attr.demo_value)
      .map((attr) => [attr.credential_attribute_tag, attr.demo_value!])
  );

export function DemoCredentialCard({ credential }: Props) {
  const hasDemoValues = credential.attributes.some((attr) => attr.demo_value);
  // Autofill with the curated demo values by default; the toggle clears them
  // so testers can enter their own.
  const [autofilled, setAutofilled] = useState(true);
  const [attributeValues, setAttributeValues] = useState<{
    [key: string]: string;
  }>(() => buildDemoValues(credential));
  const [loading, setLoading] = useState(false);

  const handleChange = (id: string, value: string) => {
    setAttributeValues((prev) => ({ ...prev, [id]: value }));
  };

  const toggleAutofill = () => {
    if (autofilled) {
      setAttributeValues({});
      setAutofilled(false);
    } else {
      setAttributeValues(buildDemoValues(credential));
      setAutofilled(true);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Per-attribute fields are optional: a card can be issued without filling
    // in every field. Empty fields are omitted from issuance entirely. Only
    // genuinely required (non-optional) attributes must still be filled in.
    const attributes: { [key: string]: string } = {};
    const missingRequired: string[] = [];
    for (const attr of credential.attributes) {
      const value = (attributeValues[attr.credential_attribute_tag] ?? "").trim();
      if (value) {
        attributes[attr.credential_attribute_tag] = value;
      } else if (!attr.optional) {
        missingRequired.push(attr.name_en);
      }
    }
    if (missingRequired.length > 0) {
      toast.error(
        `Please fill in the required field(s): ${missingRequired.join(", ")}.`
      );
      return;
    }
    try {
      setLoading(true);
      const yivi: any = await import("@privacybydesign/yivi-frontend");
      const popup = yivi.newPopup({
        debugging: import.meta.env.DEV,
        language: "en",
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
              attributes,
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
      {hasDemoValues && (
        <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
          <div>
            <p className="text-sm font-medium">Autofill demo values</p>
            <p className="text-xs text-gray-500">
              {autofilled
                ? "Fields are pre-filled with example data. Clear them to enter your own."
                : "Fields are empty. Restore the example data at any time."}
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={toggleAutofill}
            aria-pressed={autofilled}
          >
            {autofilled ? "Clear all fields" : "Restore demo values"}
          </Button>
        </div>
      )}
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
