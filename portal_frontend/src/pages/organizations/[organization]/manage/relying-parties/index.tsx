"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { RelyingParty } from "@/src/models/relying-party";
import { fetchDetailedRelyingParties } from "@/src/actions/manage-relying-party";
import ManageRelyingPartyInformationForm from "@/src/components/forms/relying-party/information";
import ManageOrganizationLayout from "@/src/components/layout/manage-organization";
import { Button } from "@/src/components/ui/button";
import { fetchOrganization } from "@/src/actions/manage-organization";

export default function RelyingParties() {
  const [message, setMessage] = useState<string | null>(null);
  const slug = useParams()?.organization;
  const [relyingParties, setRelyingParties] = useState<RelyingParty[]>([]);
  const [selectedRelyingParty, setSelectedRelyingParty] =
    useState<RelyingParty>();
  const [isCreatingNew, setIsCreatingNew] = useState(false);

  useEffect(() => {
    if (slug) {
      fetchOrganization(slug as string).then();
      fetchDetailedRelyingParties(slug as string).then(setRelyingParties);
    }
  }, [slug]);

  const handleEdit = (rp: RelyingParty) => {
    setSelectedRelyingParty(rp);
    setIsCreatingNew(false);
  };

  const handleCreate = () => {
    setSelectedRelyingParty(undefined);
    setIsCreatingNew(true);
  };

  const handleCancel = () => {
    setSelectedRelyingParty(undefined);
    setIsCreatingNew(false);
    console.log("Cancelled");
  };

  return (
    <div className="space-y-6">
      {message && (
        <div className="text-green-700 bg-green-100 border border-green-300 px-4 py-2 rounded-md">
          {message}
        </div>
      )}

      <div className="space-y-4">
        {relyingParties.map((rp) => (
          <div key={rp.rp_slug} className="space-y-2">
            <div
              className="border rounded p-4 hover:bg-muted cursor-pointer w-full"
              onClick={() => handleEdit(rp)}
            >
              <div className="font-medium text-lg">{rp.rp_slug}</div>
              <div className="text-sm text-muted-foreground">
                {rp.hostnames?.[0]?.hostname}
              </div>
            </div>

            {selectedRelyingParty?.rp_slug === rp.rp_slug && (
              <FormCard>
                <ManageRelyingPartyInformationForm
                  relying_party={rp}
                  organizationSlug={slug as string}
                  key={rp.rp_slug}
                  onCancel={handleCancel}
                  onSuccess={(type) => {
                    if (type === "nochange") {
                      setMessage("No changes detected.");
                    } else if (type === "updated") {
                      setMessage("Changes applied successfully.");
                    } else {
                      setMessage(`Unexpected result: ${type}`);
                    }
                    handleCancel();
                    setTimeout(() => setMessage(null), 3000);
                  }}
                />
              </FormCard>
            )}
          </div>
        ))}
      </div>

      <div>
        <Button variant="secondary" onClick={handleCreate}>
          Create New Relying Party
        </Button>
      </div>

      {isCreatingNew && (
        <FormCard>
          <ManageRelyingPartyInformationForm
            organizationSlug={slug as string}
            key="new"
            relying_party={undefined}
            onCancel={handleCancel}
            onSuccess={(type) => {
              if (type === "nochange") {
                setMessage("No changes detected.");
              } else if (type === "created") {
                setMessage("New relying party created successfully.");
              } else {
                setMessage(`Unexpected result: ${type}`);
              }
              // handleCancel();
              setTimeout(() => setMessage(null), 3000);
            }}
          />
        </FormCard>
      )}
    </div>
  );
}

function FormCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="border rounded p-4 w-full bg-muted/50 shadow-sm mt-6">
      {children}
    </div>
  );
}

RelyingParties.getLayout = ManageOrganizationLayout;
