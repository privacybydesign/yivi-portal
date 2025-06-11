import { fetchOrganization } from "@/actions/manage-organization";
import ManageOrganizationInformationForm from "@/components/forms/organization/information";
import { Separator } from "@/components/ui/separator";
import type { Organization } from "@/models/organization";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import { Badge } from "@/components/ui/badge";

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
    <>
      <ManageOrganizationLayout>
        <div className="space-y-6 ">
          <div>
            <h2 className="text-lg font-medium">Basic information</h2>
            <p className="text-sm text-muted-foreground">
              Update your organization&apos;s basic information.
            </p>
          </div>
          {organization && (
            <>
              {organization.is_verified === true && (
                <div className="flex items-center gap-2">
                  <Badge
                    variant="secondary"
                    className="bg-green-100 text-green-800"
                  >
                    Verified
                  </Badge>
                </div>
              )}
              {organization.is_verified === false && (
                <div className="flex flex-col gap-1">
                  <Badge
                    variant="secondary"
                    className="bg-yellow-100 text-yellow-800"
                  >
                    Pending verification
                  </Badge>
                  <div className="text-sm text-muted-foreground pl-1 italic">
                    Your organization details is waiting to be reviewed. This
                    means it won't be publicly visible until it is verified.
                  </div>
                </div>
              )}
            </>
          )}

          <Separator />
          {organization ? (
            <ManageOrganizationInformationForm
              organization={organization}
              editMode={true}
            />
          ) : (
            <p>Loading organization...</p>
          )}
        </div>
      </ManageOrganizationLayout>
    </>
  );
}
