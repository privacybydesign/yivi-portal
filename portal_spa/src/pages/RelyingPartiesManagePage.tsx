import { useState } from "react";
import { useParams } from "react-router-dom";
import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";
import { registerRelyingParty } from "@/actions/manage-relying-party";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import RelyingPartyListEdit from "@/components/forms/relying-party/RelyingPartyListEdit";
import { Button } from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import RelyingPartyTabs from "@/components/forms/relying-party/RelyingPartyTabs";
import { RelyingPartyContext } from "@/contexts/relying-party/RelyingPartyContext";

// This data will be used to prefill the Relying Party create form
const initialData: RelyingPartyFormData = {
  rp_slug: "",
  context_description_en: "",
  context_description_nl: "",
  hostnames: [{ hostname: "" }],
  attributes: [
    {
      credential_id: -1,
      credential_attribute_id: "",
      reason_en: "",
      reason_nl: "",
    },
  ],
  ready: false,
};

export default function RelyingPartyManager() {
  const params = useParams();
  const organizationSlug = params?.organization as string;
  const [saving, setSaving] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [globalError, setGlobalError] = useState<string | undefined>();
  const [isCreating, setIsCreating] = useState(false);

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
        <RelyingPartyListEdit />

        <div className="mt-6">
          <Dialog open={isCreating} onOpenChange={setIsCreating}>
            <DialogTrigger asChild>
              <Button variant="default">Add a new relying party</Button>
            </DialogTrigger>

            <DialogContent className="sm:max-w-2xl sm:max-h-[90vh] flex flex-col">
              <DialogHeader className="flex-shrink-0">
                <DialogTitle>Add a new relying party</DialogTitle>
                <DialogDescription>
                  Fill in the details for the relying party you want to add.
                </DialogDescription>
              </DialogHeader>
              <div className="flex-1 overflow-y-auto pr-2">
                <RelyingPartyContext.Provider
                  value={{
                    isEditMode: false,
                    defaultValues: initialData,
                    onSubmit: handleSave,
                    serverErrors: fieldErrors,
                    globalError: globalError || "",
                    isSaving: saving,
                    onClose: () => setIsCreating(false),
                  }}
                >
                  <RelyingPartyTabs />
                </RelyingPartyContext.Provider>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </>
    </ManageOrganizationLayout>
  );
}

RelyingPartyManager.getLayout = ManageOrganizationLayout;
