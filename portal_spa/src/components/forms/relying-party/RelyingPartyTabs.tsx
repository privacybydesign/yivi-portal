import { Button } from "@/components/ui/button";
import { useState } from "react";
import DnsChallenges from "./child-components/DNSCheck";
import RelyingPartyForm from "./child-components/RelyingPartyForm";
import { useRelyingParty } from "@/contexts/relying-party/RelyingPartyContext";

export default function RelyingPartyTabs() {
  const { defaultValues, isEditMode } = useRelyingParty();

  const hasValidHostnames =
    isEditMode &&
    Array.isArray(defaultValues.hostnames) &&
    defaultValues.hostnames.some(
      (h: { hostname?: string }) => h.hostname?.trim() !== ""
    );

  const [activeTab, setActiveTab] = useState<"form-tab" | "dns-tab">(
    "form-tab"
  );

  return (
    <>
      <div className="flex gap-4 mb-6">
        <Button
          variant={activeTab === "form-tab" ? "default" : "outline"}
          onClick={() => setActiveTab("form-tab")}
        >
          Relying party details
        </Button>
        <Button
          variant={activeTab === "dns-tab" ? "default" : "outline"}
          onClick={() => setActiveTab("dns-tab")}
          disabled={!hasValidHostnames}
        >
          DNS check
        </Button>
      </div>

      {activeTab === "form-tab" ? (
        <RelyingPartyForm />
      ) : (
        <DnsChallenges hostnames={defaultValues.hostnames} />
      )}
    </>
  );
}
