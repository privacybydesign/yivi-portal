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
import DjangoFieldErrors from "@/components/custom/DjangoErrorList";
import { Separator } from "@/components/ui/separator";

// This data will be used to prefill the Relying Party create form
const initialData: RelyingPartyFormData = {
  rp_slug: "",
  context_description_en: "",
  context_description_nl: "",
  hostnames: [{ hostname: "" }],
  attributes: [
    {
      credential_id: -1,
      credential_attribute_tag: "",
      reason_en: "",
      reason_nl: "",
    },
  ],
  ready: false,
};

export default function RelyingPartyManager() {
  const params = useParams();
  const organizationSlug = params?.organization as string;
  const [isCreating, setIsCreating] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const handleSave = async (data: RelyingPartyFormData) => {
    setIsCreating(true);
    const result = await registerRelyingParty(organizationSlug, data);
    setIsCreating(false);

    if (!result.success) {
      toast.error("Error creating relying party", {
        description: result.fieldErrors ? (
          <DjangoFieldErrors errors={result.fieldErrors} />
        ) : (
          result.globalError
        ),
      });
    } else {
      setIsOpen(false);
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
      <div className="space-y-6">
        <div className="flex flex-wrap gap-4 justify-between items-center">
          <div>
            <h2 className="text-lg font-medium">Relying parties</h2>
            <p className="text-sm text-muted-foreground">
              Update your organization's relying parties.
            </p>
          </div>

          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="default">Add relying party</Button>
            </DialogTrigger>

            <DialogContent>
              <DialogHeader>
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
                    isProcessing: isCreating,
                    onClose: () => setIsOpen(false),
                  }}
                >
                  <RelyingPartyTabs />
                </RelyingPartyContext.Provider>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <Separator />

        <RelyingPartyListEdit />
      </div>
    </ManageOrganizationLayout>
  );
}

RelyingPartyManager.getLayout = ManageOrganizationLayout;
