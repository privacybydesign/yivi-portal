import { fetchOrganization } from "@/actions/manage-organization";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import { Separator } from "@/components/ui/separator";
import type { Organization } from "@/models/organization";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

export default function AttestationProvider() {
  const slug = useParams()?.organization;
  const [organization, setOrganization] = useState<Organization>();

  useEffect(() => {
    if (slug) {
      fetchOrganization(slug as string).then((response) =>
        setOrganization(response?.data)
      );
    }
  }, [slug]);

  return (
    <ManageOrganizationLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-medium">Attestation providers (TODO)</h2>
        </div>
        <Separator />
        <div>{organization?.name_en}</div>
      </div>
    </ManageOrganizationLayout>
  );
}

AttestationProvider.getLayout = ManageOrganizationLayout;
