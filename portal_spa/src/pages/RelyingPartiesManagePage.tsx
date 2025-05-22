import { useState } from "react";
import { useParams } from "react-router-dom";
import RelyingPartyForm from "@/components/forms/relying-party/information";
import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";
import { registerRelyingParty } from "@/actions/manage-relying-party";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import RelyingPartyList from "@/components/forms/relying-party/relying-party-list";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const initialData: RelyingPartyFormData = {
  rp_slug: "",
  environment: "",
  context_description_en: "",
  context_description_nl: "",
  hostnames: [{ hostname: "" }],
  attributes: [
    {
      credential_id: undefined,
      credential_attribute_name: "",
      reason_en: "",
      reason_nl: "",
    },
  ],
};

export default function RelyingPartyManager() {
  const params = useParams();
  const organizationSlug = params?.organization as string;
  const [saving, setSaving] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [globalError, setGlobalError] = useState<string | undefined>();
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateRP = () => {
    setIsCreating(true);
    setFieldErrors({});
    setGlobalError(undefined);
  };

  const handleCancel = () => {
    setIsCreating(false);
    setFieldErrors({});
    setGlobalError(undefined);
  };

  const handleSave = async (data: RelyingPartyFormData) => {
    setSaving(true);
    const result = await registerRelyingParty(organizationSlug, data);
    setSaving(false);

    if (!result.success) {
      setFieldErrors(result.fieldErrors || {});
      setGlobalError(result.globalError);
    } else {
      setFieldErrors({});
      setGlobalError(undefined);
      setIsCreating(false);
      toast.success("Relying Party Created", {
        description: "The relying party has been created successfully.",
      });
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    }
  };

  return (
    <ManageOrganizationLayout>
      <>
        <RelyingPartyList />

        {!isCreating && (
          <div className="mt-6">
            <Button variant="default" onClick={handleCreateRP}>
              Create New Relying Party
            </Button>
          </div>
        )}

        {isCreating && (
          <div className="mt-6 border rounded p-4 bg-muted/30">
            <RelyingPartyForm
              defaultValues={initialData}
              onSubmit={handleSave}
              serverErrors={fieldErrors}
              globalError={globalError || ""}
              isSaving={saving}
              isEditMode={false}
            />
            <div className="mt-4">
              <Button variant="outline" onClick={handleCancel}>
                Cancel
              </Button>
            </div>
          </div>
        )}
      </>
    </ManageOrganizationLayout>
  );
}

RelyingPartyManager.getLayout = ManageOrganizationLayout;
