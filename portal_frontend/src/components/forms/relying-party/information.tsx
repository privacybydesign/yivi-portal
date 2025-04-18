"use client";

import { useState } from "react";
import { Button } from "@/src/components/ui/button";
import { Input } from "@/src/components/ui/input";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
} from "@/src/components/ui/form";
import { Label } from "@/src/components/ui/label";
import {
  registerRelyingParty,
  updateRelyingParty,
  RelyingPartyInputs,
  RelyingPartyFormState,
} from "@/src/actions/manage-relying-party";
import { generateSlug } from "@/lib/utils";
import { useForm, useFieldArray } from "react-hook-form";
import { RelyingParty } from "@/src/models/relying-party";
import DnsChallenges from "@/src/components/forms/relying-party/dnscheck";

type ManageRelyingPartyInformationFormProps = {
  organizationSlug: string;
  relying_party?: RelyingParty;
  onCancel: () => void;
  onSuccess: (type: "updated" | "created" | "nochange") => void;
};

function getChangedFields<T extends RelyingPartyInputs>(
  original: T,
  updated: T
): Partial<T> {
  const diff: Partial<T> = {};
  for (const key in updated) {
    const originalVal = original[key];
    const updatedVal = updated[key];
    if (Array.isArray(originalVal) && Array.isArray(updatedVal)) {
      if (JSON.stringify(originalVal) !== JSON.stringify(updatedVal)) {
        diff[key] = updatedVal;
      }
    } else if (originalVal !== updatedVal) {
      diff[key] = updatedVal;
    }
  }
  return diff;
}

export default function ManageRelyingPartyInformationForm({
  organizationSlug,
  relying_party,
  onCancel,
  onSuccess,
}: ManageRelyingPartyInformationFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"form" | "result">("form");
  const [formResult, setFormResult] = useState<RelyingPartyFormState | null>(
    null
  );
  const hostnames = formResult?.hostnames ?? relying_party?.hostnames ?? [];

  const isEdit = Boolean(relying_party);

  const initialValues: RelyingPartyInputs = {
    rp_slug: relying_party?.rp_slug ?? "",
    hostnames:
      relying_party?.hostnames?.map((h) =>
        typeof h === "string" ? { hostname: h } : h
      ) ?? [],
    environment: relying_party?.environment ?? "",
    context_description_en: relying_party?.context_description_en ?? "",
    context_description_nl: relying_party?.context_description_nl ?? "",
    attributes: relying_party?.attributes?.length
      ? relying_party.attributes
      : [{ credential_attribute_name: "", reason_en: "", reason_nl: "" }],
  };

  const form = useForm<RelyingPartyInputs>({ defaultValues: initialValues });

  const {
    fields: hostnameFields,
    append: addHostname,
    remove: removeHostname,
  } = useFieldArray({
    control: form.control,
    name: "hostnames",
  });

  const {
    fields: attributeFields,
    append: addAttribute,
    remove: removeAttribute,
  } = useFieldArray({
    control: form.control,
    name: "attributes",
  });

  const handleSubmit = async (values: RelyingPartyInputs) => {
    setIsSubmitting(true);
    setFormError(null);

    try {
      let response: RelyingPartyFormState;

      if (isEdit) {
        const diff = getChangedFields(initialValues, values);

        if (Object.keys(diff).length === 0) {
          setFormResult({
            values,
            errors: {},
            success: true,
            hostnames: values.hostnames,
          });
          setActiveTab("result");
          onSuccess("nochange");
          return;
        }

        response = await updateRelyingParty(organizationSlug, {
          ...initialValues,
          ...diff,
        });

        if (response.success) onSuccess("updated");
      } else {
        response = await registerRelyingParty(organizationSlug, values);
        if (response.success) onSuccess("created");
      }

      setFormResult({
        ...response,
      });
      setActiveTab("result");

      if (response.globalError) {
        setFormError(response.globalError);
      } else if (response.errors) {
        Object.entries(response.errors).forEach(([field, error]) => {
          if (error?.message) {
            form.setError(field as keyof RelyingPartyInputs, {
              type: "server",
              message: error.message,
            });
          }
        });
      }
    } catch (error) {
      console.error("Form submission error:", error);
      setFormError("An unexpected error occurred. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab("form")}
          className={`rounded-lg px-4 py-2 border shadow-sm text-sm font-medium ${
            activeTab === "form"
              ? "bg-white border-blue-500 text-blue-700"
              : "bg-muted text-muted-foreground"
          }`}
        >
          Relying Party Details
        </button>

        <button
          onClick={() => relying_party && setActiveTab("result")}
          className={`rounded-lg px-4 py-2 border shadow-sm text-sm font-medium ${
            activeTab === "result"
              ? "bg-white border-blue-500 text-blue-700"
              : "bg-muted text-muted-foreground"
          } ${!relying_party ? "opacity-50 cursor-not-allowed" : ""}`}
          disabled={!relying_party}
        >
          DNS Check
        </button>
      </div>

      {activeTab === "form" && (
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-6"
          >
            <FormField
              control={form.control}
              name="rp_slug"
              render={({ field: { onBlur, ...field } }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>Slug</Label>
                    <FormDescription>
                      Slug you want to use for this relying party.
                    </FormDescription>
                  </div>
                  <div>
                    <FormControl>
                      <Input
                        {...field}
                        onBlur={(event) => {
                          if (!form.control.getFieldState("rp_slug").isDirty) {
                            form.setValue(
                              "rp_slug",
                              generateSlug(event.target.value.trim())
                            );
                          }
                          onBlur();
                        }}
                      />
                    </FormControl>
                  </div>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="environment"
              render={({ field }) => (
                <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                  <div className="py-1">
                    <Label>Environment</Label>
                    <FormDescription>
                      Choose where this RP will run.
                    </FormDescription>
                  </div>
                  <div>
                    <FormControl>
                      <select
                        {...field}
                        className="input w-full border px-3 py-2 rounded"
                      >
                        <option value="">Select environment</option>
                        <option value="production">Production</option>
                        <option value="demo">Demo</option>
                      </select>
                    </FormControl>
                  </div>
                </FormItem>
              )}
            />

            {["context_description_en", "context_description_nl"].map(
              (langKey) => (
                <FormField
                  key={langKey}
                  control={form.control}
                  name={langKey as keyof RelyingPartyInputs}
                  render={({ field }) => (
                    <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
                      <div className="py-1">
                        <Label>
                          {langKey.endsWith("en") ? "English" : "Dutch"} Context
                          Description
                        </Label>
                      </div>
                      <div>
                        <FormControl>
                          <Input
                            {...field}
                            value={
                              typeof field.value === "string" ? field.value : ""
                            }
                          />
                        </FormControl>
                      </div>
                    </FormItem>
                  )}
                />
              )
            )}

            <div className="space-y-2">
              <Label>Hostnames</Label>
              <div className="space-y-3">
                {hostnameFields.map((field, index) => (
                  <FormField
                    key={field.id}
                    control={form.control}
                    name={`hostnames.${index}.hostname`}
                    render={({ field }) => (
                      <FormItem className="flex items-center gap-2">
                        <FormControl>
                          <Input
                            {...field}
                            placeholder={`Hostname ${index + 1}`}
                          />
                        </FormControl>
                        <Button
                          type="button"
                          variant="destructive"
                          onClick={() => removeHostname(index)}
                        >
                          Remove
                        </Button>
                      </FormItem>
                    )}
                  />
                ))}
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => addHostname({ hostname: "" })}
                >
                  Add Hostname
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              <Label>Attributes</Label>
              {attributeFields.map((field, index) => (
                <div
                  key={field.id}
                  className="space-y-4 rounded-xl border p-4 shadow-sm bg-white"
                >
                  <div className="grid md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name={`attributes.${index}.credential_attribute_name`}
                      render={({ field }) => (
                        <FormItem>
                          <Label>Attribute Name</Label>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="e.g. pbdf.pbdf.email.email"
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name={`attributes.${index}.reason_en`}
                      render={({ field }) => (
                        <FormItem>
                          <Label>English Reason </Label>
                          <FormControl>
                            <Input {...field} placeholder="Why it's needed" />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name={`attributes.${index}.reason_nl`}
                      render={({ field }) => (
                        <FormItem>
                          <Label> Dutch Reason</Label>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Waarom het nodig is"
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={() => removeAttribute(index)}
                    >
                      Remove Attribute
                    </Button>
                  </div>
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  addAttribute({
                    credential_attribute_name: "",
                    reason_en: "",
                    reason_nl: "",
                  })
                }
              >
                Add Attribute
              </Button>
            </div>

            {formError && (
              <div className="text-sm text-red-600 font-medium">
                {formError}
              </div>
            )}

            <div className="flex justify-between items-center">
              <Button variant="ghost" onClick={onCancel}>
                Close
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Submitting..." : "Submit"}
              </Button>
            </div>
          </form>
        </Form>
      )}

      {activeTab === "result" && <DnsChallenges hostnames={hostnames} />}
    </>
  );
}
