"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { Organization } from "@/src/models/organization";
import { RelyingParty } from "@/src/models/relying-party";
import { fetchOrganization } from "@/src/actions/manage-organization";
import { fetchRelyingPartiesForOrganization } from "@/src/actions/manage-relying-party";

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

  useEffect(() => {
    if (slug) {
      fetchOrganization(slug as string).then((response) =>
        setOrganization(response?.data)
      );

      fetchRelyingPartiesForOrganization(slug as string).then(
        (response: { data: RelyingParty[] }) =>
          setRelyingParties(response?.data ?? [])
      );
    }
  }, [slug]);
  return (
    <>
      <div className="space-y-6">
        <h2 className="text-lg font-medium">Relying Parties</h2>
        <Separator />
        <p className="text-muted-foreground">
          Organization: {organization?.name_en}
        </p>
        <div className="grid md:grid-cols-2 gap-8">
          {/* List of Relying Parties */}
          <div className="space-y-4">
            {relyingParties.map((rp) => (
              <div
                key={rp.rp_slug}
                className="flex justify-between items-center border p-3 rounded hover:bg-muted cursor-pointer"
                onClick={() => setSelectedRelyingParty(rp)}
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
              onClick={() => setSelectedRelyingParty(undefined)}
            >
              + New Relying Party
            </Button>
          </div>

          {/* Detail Form */}
          <div>
            <ManageRelyingPartyInformationForm
              relying_party={selectedRelyingParty}
            />
          </div>
        </div>
      </div>
    </>
  );
}

RelyingParties.getLayout = ManageOrganizationLayout;
