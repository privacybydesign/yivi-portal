import { toast } from "sonner";
import {
  fetchMaintainersForOrganization,
  deleteMaintainerFromOrganization,
} from "@/actions/manage-maintainer";
import { fetchOrganization } from "@/actions/manage-organization";
import AddOrganizationMaintainerInformationForm from "@/components/forms/organization/maintainer";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import type { Maintainer } from "@/models/maintainer";
import type { Organization } from "@/models/organization";
import { AxiosError } from "axios";
import { X } from "lucide-react";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

/** The organization's maintainers, or none after telling the user it failed. */
const loadMaintainers = async (
  organisationSlug: string,
): Promise<Maintainer[]> => {
  try {
    const response = await fetchMaintainersForOrganization(organisationSlug);
    return response?.data ?? [];
  } catch (e: unknown) {
    toast.error("Something went wrong", {
      description:
        e instanceof AxiosError
          ? e.message
          : "Please try again at a later time.",
    });
    console.error(e);
    return [];
  }
};

export default function MaintainerManagePage() {
  const slug = useParams()?.organization;
  const [maintainers, setMaintainers] = useState<Maintainer[]>([]);
  const [organization, setOrganization] = useState<Organization>();

  const refreshMaintersForOrganization = (organisationSlug: string) =>
    loadMaintainers(organisationSlug).then(setMaintainers);

  useEffect(() => {
    if (!slug) return;
    // State is only set from the callbacks, and not for a slug left behind.
    let current = true;
    fetchOrganization(slug).then(
      (response) => current && setOrganization(response?.data),
    );
    loadMaintainers(slug).then((list) => current && setMaintainers(list));
    return () => {
      current = false;
    };
  }, [slug]);

  const deleteMaintainer = async (maintainer: Maintainer) => {
    const { success, message } = await deleteMaintainerFromOrganization(
      maintainer,
      organization,
    );
    refreshMaintersForOrganization(organization?.slug ?? "");

    if (success) {
      toast.success("Maintainer deleted successfully");
    } else {
      toast.error("Something went wrong", {
        description: message,
      });
    }
  };

  return (
    <ManageOrganizationLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap gap-4 justify-between items-center">
          <div>
            <h2 className="text-lg font-medium">Maintainers</h2>
            <p className="text-sm text-muted-foreground">
              Update your organization's maintainers.
            </p>
          </div>
          {organization && (
            <AddOrganizationMaintainerInformationForm
              organization={organization}
              onCreate={refreshMaintersForOrganization}
            ></AddOrganizationMaintainerInformationForm>
          )}
        </div>

        <Separator />

        <div className="space-y-4">
          {maintainers.map((maintainer) => (
            <div key={maintainer.id} className="space-y-2">
              <div className="flex justify-between items-center border p-3 rounded hover:bg-muted cursor-pointer">
                <div>
                  <div className="font-medium">{maintainer.email}</div>
                  <div className="text-sm text-muted-foreground">
                    {maintainer.role}
                  </div>
                </div>
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={() => deleteMaintainer(maintainer)}
                >
                  <X />
                  <span className="sr-only"></span>
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </ManageOrganizationLayout>
  );
}

MaintainerManagePage.getLayout = ManageOrganizationLayout;
