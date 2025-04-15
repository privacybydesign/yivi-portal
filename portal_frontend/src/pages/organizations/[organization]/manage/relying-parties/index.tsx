"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { Organization } from "@/src/models/organization";
import { RelyingParty } from "@/src/models/relying-party";
import { fetchOrganization } from "@/src/actions/manage-organization";
import { fetchDetailedRelyingPartiesForOrganization } from "@/src/actions/manage-relying-party";

import ManageRelyingPartyInformationForm from "@/src/components/forms/relying-party/information";
import ManageOrganizationLayout from "@/src/components/layout/manage-organization";
import { Button } from "@/src/components/ui/button";
import { Separator } from "@/src/components/ui/separator";

export default function RelyingParties() {
  const slug = useParams()?.organization;
  const [organization, setOrganization] = useState<Organization>();
  const [relyingParties, setRelyingParties] = useState<RelyingParty[]>([]);
  const [selectedRelyingParty, setSelectedRelyingParty] = useState<
    RelyingParty | undefined
  >();
  const [isCreatingNew, setIsCreatingNew] = useState<boolean>(false);

  useEffect(() => {
    if (slug) {
      fetchOrganization(slug as string).then((response) =>
        setOrganization(response?.data)
      );

      fetchDetailedRelyingPartiesForOrganization(slug as string).then(
        (detailedList) => setRelyingParties(detailedList)
      );
    }
  }, [slug]);

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-medium">Relying Parties</h2>
      <Separator />

      <div className="grid md:grid-cols-2 gap-8">
        <div className="space-y-4">
          {relyingParties.map((rp) => (
            <div
              key={rp.rp_slug}
              className="flex justify-between items-center border p-3 rounded hover:bg-muted cursor-pointer"
              onClick={() => {
                setSelectedRelyingParty(rp);
                setIsCreatingNew(false);
              }}
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
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              setSelectedRelyingParty(undefined);
              setIsCreatingNew(true);
            }}
          >
            + New Relying Party
          </Button>
        </div>
      </div>

      {(selectedRelyingParty || isCreatingNew) && (
        <div className="pt-8 border-t mt-6">
          <ManageRelyingPartyInformationForm
            relying_party={selectedRelyingParty}
          />
        </div>
      )}
    </div>
  );
}

RelyingParties.getLayout = ManageOrganizationLayout;
