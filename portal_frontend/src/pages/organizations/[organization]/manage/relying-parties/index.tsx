"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { RelyingParty } from "@/src/models/relying-party";
import { fetchDetailedRelyingParties } from "@/src/actions/manage-relying-party";
import ManageRelyingPartyInformationForm from "@/src/components/forms/relying-party/information";
import ManageOrganizationLayout from "@/src/components/layout/manage-organization";
import { Button } from "@/src/components/ui/button";
import { Separator } from "@/src/components/ui/separator";
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
      <h2 className="text-lg font-medium">Relying Parties</h2>
      <Separator />
      {message && (
        <div className="text-green-700 bg-green-100 border border-green-300 px-4 py-2 rounded-md">
          {message}
        </div>
      )}

      {/* Grid of Relying Parties */}
      <div className="grid md:grid-cols-2 gap-8">
        {relyingParties.map((rp) => (
          <div key={rp.rp_slug} className="space-y-2">
            <div
              className="flex justify-between items-center border p-3 rounded hover:bg-muted cursor-pointer"
              onClick={() => handleEdit(rp)}
            >
              <div>
                <div className="font-medium">{rp.rp_slug}</div>
                <div className="text-sm text-muted-foreground">
                  {rp.hostnames?.[0]?.hostname}
                </div>
              </div>
              <Button variant="outline" size="sm">
                Edit
              </Button>
            </div>
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
            key={"new"}
            relying_party={undefined}
            onCancel={handleCancel}
            onSuccess={(type) => {
              if (type === "nochange") {
                setMessage("No changes detected.");
                handleCancel();
              } else if (type === "updated" || type === "created") {
                setMessage(
                  type === "updated"
                    ? "Changes applied successfully."
                    : "New relying party created successfully."
                );
                handleCancel();
              }
              setTimeout(() => setMessage(null), 3000);
            }}
          />
        </FormCard>
      )}

      {selectedRelyingParty && (
        <FormCard>
          <ManageRelyingPartyInformationForm
            relying_party={selectedRelyingParty}
            organizationSlug={slug as string}
            onCancel={handleCancel}
            onSuccess={(type) => {
              if (type === "created") {
                setMessage("New relying party created successfully.");
                handleCancel();
              }
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
