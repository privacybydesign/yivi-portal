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
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useEffect, useState } from "react";
import { fetchCredentials } from "@/actions/manage-relying-party";
import type { Credential } from "@/models/credential";
import DnsChallenges from "@/components/forms/relying-party/dnscheck";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";
import ContextDescription from "./form-components/ContextDescription";
import Hostnames from "./form-components/Hostnames";
import { CredentialAttributes } from "./form-components/CredentialAttributes";
import ReadyCheckbox from "./form-components/ReadyCheckbox";

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

            {/* Hostnames */}
            <Hostnames
              hostnameFields={hostnameFields}
              register={register}
              removeHostname={removeHostname}
              appendHostname={appendHostname}
              errors={errors}
            />

            {/* Context Description */}
            <ContextDescription control={control} />

            {/* Credential Selection and Attributes */}
            <CredentialAttributes
              attrFields={attrFields}
              form={form}
              credentials={credentials}
              appendAttr={appendAttr}
              removeAttr={removeAttr}
            />

            <ReadyCheckbox control={control} serverErrors={serverErrors} />

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
