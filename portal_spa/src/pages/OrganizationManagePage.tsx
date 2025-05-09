import { fetchOrganization } from "@/actions/manage-organization";
import ManageOrganizationInformationForm from "@/components/forms/organization/information";
import { Separator } from "@/components/ui/separator";
import type { Organization } from "@/models/organization";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";

export default function ManageLayout() {
  const { organization: slug } = useParams();
  const [organization, setOrganization] = useState<Organization | null>(null);

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
          <h2 className="text-lg font-medium">Basic information</h2>
          <p className="text-sm text-muted-foreground">
            Update your organization&apos;s basic information.
          </p>
        </div>
        <Separator />
        {organization ? (
          <ManageOrganizationInformationForm organization={organization} />
        ) : (
          <p>Loading organization...</p>
        )}
      </div>
    </ManageOrganizationLayout>
  );
}
