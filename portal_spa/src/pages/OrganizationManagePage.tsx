import { fetchOrganization } from "@/actions/manage-organization";
import OrganizationForm from "@/components/forms/organization/OrganizationForm";
import { Separator } from "@/components/ui/separator";
import type { Organization } from "@/models/organization";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import { Badge } from "@/components/ui/badge";
import { useTranslation } from "react-i18next";

export default function ManageLayout() {
  const { organization: slug } = useParams();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const { t } = useTranslation();

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
            <h2 className="text-lg font-medium">
              {t("manage.basic_info_heading")}
            </h2>
            <p className="text-sm text-muted-foreground">
              {t("manage.update_basic_info")}
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
                    {t("organization.verified")}
                  </Badge>
                </div>
              )}
              {organization.is_verified === false && (
                <div className="flex flex-col gap-1">
                  <Badge
                    variant="secondary"
                    className="bg-yellow-100 text-yellow-800"
                  >
                    {t("manage.pending_verification")}
                  </Badge>
                  <div className="text-sm text-muted-foreground pl-1 italic">
                    {t("manage.pending_verification_desc")}
                  </div>
                </div>
              )}
            </>
          )}

          <Separator />
          {organization ? (
            <OrganizationForm
              organization={organization}
              pendingButtonLabel={"Saving..."}
              submitButtonLabel={"Save"}
            />
          ) : (
            <p>Loading organization...</p>
          )}
        </div>
      </ManageOrganizationLayout>
    </>
  );
}
