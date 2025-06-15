import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { RelyingPartySchema } from "./validation-schema";
import type { RelyingPartyFormData } from "./validation-schema";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useEffect, useState } from "react";
import { fetchCredentials } from "@/actions/manage-relying-party";
import type { Credential } from "@/models/credential";
import DnsChallenges from "@/components/forms/relying-party/dnscheck";
import CredentialAttributeFields from "@/components/custom/SelectAttributes";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";

type RelyingPartyProps =
  | {
      isEditMode: true;
      originalSlug: string;
      defaultValues: RelyingPartyFormData;
      onSubmit: (
        data: Partial<RelyingPartyFormData>,
        originalSlug: string
      ) => void;
      serverErrors?: Partial<Record<keyof RelyingPartyFormData, string>>;
      globalError?: string | undefined;
      isSaving: boolean;
      onClose?: () => void;
    }
  | {
      isEditMode: false;
      originalSlug?: never;
      defaultValues: RelyingPartyFormData;
      onSubmit: (data: RelyingPartyFormData) => void;
      serverErrors?: Partial<Record<keyof RelyingPartyFormData, string>>;
      globalError?: string | undefined;
      isSaving: boolean;
      onClose?: () => void;
    };

export default function RelyingPartyForm({
  defaultValues,
  onSubmit,
  serverErrors = {},
  globalError,
  isSaving,
  originalSlug,
  isEditMode,
  onClose,
}: RelyingPartyProps) {
  const form = useForm<RelyingPartyFormData>({
    resolver: zodResolver(RelyingPartySchema),
    defaultValues,
  });
  const hasValidHostnames =
    isEditMode &&
    Array.isArray(defaultValues.hostnames) &&
    defaultValues.hostnames.some((h) => h.hostname?.trim() !== "");

  const {
    control,
    handleSubmit,
    register,
    formState: { errors },
  } = form;

  const {
    fields: hostnameFields,
    append: appendHostname,
    remove: removeHostname,
  } = useFieldArray({ control, name: "hostnames" });

  const {
    fields: attrFields,
    append: appendAttr,
    remove: removeAttr,
  } = useFieldArray({ control, name: "attributes" });

  const [activeTab, setActiveTab] = useState<"form-tab" | "dns-tab">(
    "form-tab"
  );

  useEffect(() => {
    if (globalError) {
      toast.error("Error", {
        description: globalError,
      });
    }
  }, [globalError, toast]);

  function getChangedFormData(
    original: RelyingPartyFormData,
    current: RelyingPartyFormData
  ): Partial<RelyingPartyFormData> {
    const result: Partial<RelyingPartyFormData> = {};

    for (const key in current) {
      const typedKey = key as keyof RelyingPartyFormData;

      if (typedKey === "hostnames") {
        const originalHostnames = original.hostnames
          .map((h) => h.hostname)
          .sort();
        const currentHostnames = current.hostnames
          .map((h) => h.hostname)
          .sort();
        const isSame =
          JSON.stringify(originalHostnames) ===
          JSON.stringify(currentHostnames);
        if (!isSame) {
          result.hostnames = current.hostnames;
        }
      } else if (typedKey === "attributes") {
        const isSame =
          JSON.stringify(original.attributes) ===
          JSON.stringify(current.attributes);
        if (!isSame) {
          result.attributes = current.attributes;
        }
      } else if (
        JSON.stringify(original[typedKey]) !== JSON.stringify(current[typedKey])
      ) {
        if (typedKey === "ready") {
          result[typedKey] = current[typedKey];
        } else {
          result[typedKey] = current[typedKey];
        }
      }
    }

    return result;
  }

  const [credentials, setCredentials] = useState<Credential[]>([]);

  useEffect(() => {
    async function hydrateCredentialSelections() {
      const res = await fetchCredentials();
      if (res.success && res.data) {
        setCredentials(res.data.credentials);
      }
    }

    hydrateCredentialSelections();
  }, [defaultValues.attributes, form]);

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
        <Form {...form}>
          <form
            onSubmit={handleSubmit((formData) => {
              console.log("Form data submitted:", formData);
              if (isEditMode) {
                const payload = getChangedFormData(defaultValues, formData);
                if (Object.keys(payload).length === 0) {
                  toast("No changes detected", {
                    description: "Nothing was modified.",
                  });
                  setTimeout(() => {
                    if (typeof onClose === "function") {
                      onClose();
                    }
                  }, 100);
                  return;
                }
                (
                  onSubmit as (
                    data: Partial<RelyingPartyFormData>,
                    originalSlug: string
                  ) => void
                )(payload, originalSlug);
              } else {
                (onSubmit as (data: RelyingPartyFormData) => void)(formData);
              }
            })}
          >
            <div className="space-y-2 mt-4">
              <FormField
                control={control}
                name="rp_slug"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Relying party slug
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
                            <Info className="w-3 h-3" />
                          </div>
                        </TooltipTrigger>
                        <TooltipContent side="top">
                          <p className="text-sm">
                            This will serve as a unique identifier for your
                            relying party. Each slug must be distinct —
                            duplicate slugs are not allowed.
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage>{serverErrors.rp_slug}</FormMessage>
                  </FormItem>
                )}
              />
            </div>

            <div className="space-y-2 mt-4">
              <FormLabel className="font-medium">Hostnames</FormLabel>

              <div className="space-y-2 rounded-md">
                {hostnameFields.map((field, index) => (
                  <div key={index} className="flex gap-2 items-start">
                    {field.id !== undefined && typeof field.id === "number" && (
                      <Input
                        type="hidden"
                        {...register(`hostnames.${index}.id`, {
                          valueAsNumber: true,
                        })}
                        defaultValue={field.id}
                      />
                    )}

                    <Input
                      {...register(`hostnames.${index}.hostname`)}
                      defaultValue={field.hostname}
                      className="w-full"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeHostname(index)}
                    >
                      Remove
                    </Button>
                    <FormMessage>
                      {errors.hostnames?.[index]?.hostname?.message}
                    </FormMessage>
                  </div>
                ))}
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => appendHostname({ hostname: "" })}
              >
                Add hostname
              </Button>
            </div>

            <div className="space-y-2 mt-4">
              <FormLabel className="text-base font-medium">
                Context description
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
                      <Info className="w-3 h-3" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="text-sm">
                      Provide a short description of the context in which you're
                      using Yivi and the selected attributes. For example:
                      "Access to employee portal" or "Proof of age for alcohol
                      purchase".
                    </p>
                  </TooltipContent>
                </Tooltip>
              </FormLabel>

              <FormField
                control={control}
                name="context_description_en"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm">English</FormLabel>
                    <FormControl>
                      <Textarea {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="context_description_nl"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm">Dutch</FormLabel>
                    <FormControl>
                      <Textarea {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="space-y-2 mt-4">
              <FormLabel className="text-base font-medium">
                Credential attributes
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
                      <Info className="w-3 h-3" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="text-sm">
                      In this section, specify the Yivi credential attributes
                      you intend to request from users through this relying
                      party.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </FormLabel>

              <div className="space-y-2">
                {attrFields.map((field, index) => (
                  <div key={field.id} className="rounded-md space-y-3">
                    <CredentialAttributeFields
                      index={index}
                      credentials={credentials}
                      value={{
                        ...form.getValues(`attributes.${index}`),
                        credential_id:
                          form.getValues(`attributes.${index}.credential_id`) ??
                          -1,
                      }}
                      onChange={(updatedAttr) =>
                        form.setValue(`attributes.${index}`, updatedAttr, {
                          shouldValidate: true,
                        })
                      }
                    />

                    <div className="flex justify-end">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAttr(index)}
                      >
                        Remove attribute
                      </Button>
                    </div>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    appendAttr({
                      credential_id: undefined,
                      credential_attribute_name: "",
                      reason_en: "",
                      reason_nl: "",
                    })
                  }
                >
                  Add attribute
                </Button>
              </div>
            </div>
            <div className="space-y-2 mt-4">
              <FormField
                control={control}
                name="ready"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        id="ready-checkbox"
                      />
                    </FormControl>
                    <FormLabel
                      htmlFor="ready-checkbox"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                      Mark as ready
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 text-gray-600 cursor-pointer">
                            <Info className="w-3 h-3" />
                          </div>
                        </TooltipTrigger>
                        <TooltipContent
                          side="top"
                          className="max-w-md break-words"
                        >
                          <p className="justify-center text-sm">
                            Marking this relying party as "ready" indicates that
                            it is prepared for review and publication. You may
                            choose to leave it unmarked — in that case, your
                            registration will remain in draft form and will not
                            be finalized.
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </FormLabel>
                    <FormMessage>{serverErrors.ready}</FormMessage>
                  </FormItem>
                )}
              />
            </div>

            <div className="gap-2 mt-6 flex sm:justify-end">
              {isEditMode && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    if (typeof onClose === "function") {
                      onClose();
                    }
                  }}
                  className="h-9 text-sm"
                >
                  Cancel
                </Button>
              )}
              <Button
                type="submit"
                disabled={isSaving}
                className="h-9 px-4 text-sm"
              >
                {isSaving ? "Saving..." : "Save"}
              </Button>
            </div>
          </form>
        </Form>
      ) : (
        <DnsChallenges hostnames={defaultValues.hostnames} />
      )}
    </>
  );
}
