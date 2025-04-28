"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  fetchAllRelyingParties,
  fetchRelyingParty,
  updateRelyingParty,
} from "@/src/actions/manage-relying-party";
import { RelyingParty } from "@/src/models/relying-party";
import { Button } from "@/src/components/ui/button";
import RelyingPartyForm from "./information";
import { toast } from "@/hooks/use-toast";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/src/components/ui/select";

type FetchRelyingPartiesResponse = {
  relying_parties: RelyingParty[];
};

export default function RelyingPartyList() {
  const params = useParams();
  const organizationSlug = params?.organization as string;

  const [environment, setEnvironment] = useState("demo");
  const [relyingParties, setRelyingParties] = useState<RelyingParty[]>([]);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingSlug, setEditingRPSlug] = useState<string | null>(null);
  const [editingRP, setEditingRP] = useState<RelyingParty | null>(null);
  const [editingLoading, setEditingLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    if (!organizationSlug) return;

    setLoading(true);
    const result = await fetchAllRelyingParties(organizationSlug);
    setLoading(false);

    if (!result.success) {
      setGlobalError(result.globalError || "Could not load relying parties.");
      return;
    }

    const { relying_parties } = result.data as FetchRelyingPartiesResponse;

    const order = { production: 0, demo: 1 };
    const sorted = [...(relying_parties || [])].sort(
      (a, b) =>
        order[a.environment as keyof typeof order] -
        order[b.environment as keyof typeof order]
    );

    setRelyingParties(sorted);
  }, [organizationSlug]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredRelyingParties = relyingParties.filter(
    (rp) => rp.environment === environment
  );

  const handleEdit = async (slug: string) => {
    if (editingSlug === slug) {
      setEditingRPSlug(null);
      setEditingRP(null);
      return;
    }

    const rp = relyingParties.find((r) => r.rp_slug === slug);
    if (!rp) {
      toast({
        title: "Error",
        description: "Relying party not found.",
        variant: "destructive",
      });
      return;
    }

    setEditingLoading(true);
    setEditingRPSlug(slug);
    const result = await fetchRelyingParty(
      organizationSlug,
      slug,
      rp.environment
    );
    setEditingLoading(false);

    if (!result.success) {
      toast({
        title: "Error",
        description: result.globalError || "Failed to fetch RP details.",
        variant: "destructive",
      });
      setEditingRPSlug(null);
      return;
    }

    setEditingRP(result.data as RelyingParty);
  };
  const handleCancelEdit = () => {
    setEditingRPSlug(null);
    setEditingRP(null);
  };

  const handleSuccess = (type: "updated" | "nochange" | "error") => {
    if (type === "updated") {
      toast({ title: "Success", description: "Changes saved." });
    } else if (type === "nochange") {
      toast({ title: "Info", description: "No changes detected." });
    } else {
      toast({
        title: "Error",
        description: "Something went wrong.",
        variant: "destructive",
      });
    }
  };

  if (loading) return <p>Loading...</p>;
  if (globalError) return <p className="text-red-600">Error: {globalError}</p>;

  return (
    <div>
      <div className="mb-6">
        <Select
          value={environment}
          onValueChange={(val) => setEnvironment(val)}
        >
          <SelectTrigger className="w-60">
            <SelectValue placeholder="Select environment" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="demo">Demo</SelectItem>
            <SelectItem value="production">Production</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {filteredRelyingParties.length === 0 ? (
        <p>No relying parties found for selected environment.</p>
      ) : (
        <ul className="space-y-4">
          {filteredRelyingParties.map((rp) => (
            <li key={rp.rp_slug} className="border p-4 rounded shadow-sm">
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium text-lg">{rp.rp_slug}</div>
                  <div className="text-sm text-gray-500">
                    {rp.hostnames?.map((h, i) => (
                      <div key={i}>{h.hostname}</div>
                    ))}
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={() => handleEdit(rp.rp_slug)}
                >
                  {editingSlug === rp.rp_slug ? "Cancel" : "Edit"}
                </Button>
              </div>

              {editingSlug === rp.rp_slug && (
                <div className="mt-4">
                  {editingLoading || !editingRP ? (
                    <p>Loading form...</p>
                  ) : (
                    <RelyingPartyForm
                      originalSlug={editingRP.rp_slug}
                      defaultValues={{
                        rp_slug: editingRP.rp_slug,
                        environment: editingRP.environment,
                        context_description_en:
                          editingRP.context_description_en ?? "",
                        context_description_nl:
                          editingRP.context_description_nl ?? "",
                        hostnames: editingRP.hostnames,
                        attributes: editingRP.attributes,
                      }}
                      onSubmit={async (formData, originalSlug) => {
                        setSaving(true);

                        const result = await updateRelyingParty(
                          organizationSlug,
                          formData,
                          originalSlug
                        );
                        setSaving(false);

                        if (!result.success) {
                          toast({
                            title: "Error",
                            description: result.globalError || "Update failed.",
                            variant: "destructive",
                          });
                          return;
                        }

                        handleSuccess("updated");
                        handleCancelEdit();
                        fetchData();
                      }}
                      isSaving={saving}
                      isEditMode={true}
                      onClose={handleCancelEdit}
                    />
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
