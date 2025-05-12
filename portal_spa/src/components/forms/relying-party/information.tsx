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
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "../../ui/select";
import { useEffect, useState } from "react";
import DnsChallenges from "@/components/forms/relying-party/dnscheck";

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
        result[typedKey] = current[typedKey];
      }
    }

    return result;
  }

  return (
    <>
      <div className="flex gap-4 mb-6">
        <Button
          variant={activeTab === "form-tab" ? "default" : "outline"}
          onClick={() => setActiveTab("form-tab")}
        >
          Relying Party Details
        </Button>
        <Button
          variant={activeTab === "dns-tab" ? "default" : "outline"}
          onClick={() => setActiveTab("dns-tab")}
          disabled={!hasValidHostnames}
        >
          DNS Check
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
                    <FormLabel>Relying Party Slug</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage>{serverErrors.rp_slug}</FormMessage>
                  </FormItem>
                )}
              />
            </div>
            <div className="space-y-2 mt-4">
              <FormField
                control={control}
                name="environment"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Environment</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an environment" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="demo">Demo</SelectItem>
                        <SelectItem value="production">Production</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="space-y-2 mt-4">
              <FormLabel className="text-base font-medium">
                Context Description
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
                Add Hostname
              </Button>
            </div>

            <div className="space-y-2 mt-4">
              <FormLabel className="font-bold">Credential Attributes</FormLabel>

              <div className="space-y-2">
                {attrFields.map((field, index) => (
                  <div
                    key={field.id}
                    className="border p-4 rounded-md space-y-3"
                  >
                    <div className="grid md:grid-cols-1 gap-4">
                      <FormLabel>Attribute Name</FormLabel>
                      <Input
                        {...register(
                          `attributes.${index}.credential_attribute_name`
                        )}
                      />
                      <FormMessage>
                        {
                          errors.attributes?.[index]?.credential_attribute_name
                            ?.message
                        }
                      </FormMessage>
                    </div>
                    <FormLabel className="font-medium">Reason</FormLabel>

                    <div className="grid  gap-4">
                      <div className="grid md:grid-cols-2 gap-2">
                        <div className="space-y-2">
                          <FormLabel className="text-sm">English</FormLabel>
                          <Input
                            {...register(`attributes.${index}.reason_en`)}
                          />
                          <FormMessage>
                            {errors.attributes?.[index]?.reason_en?.message}
                          </FormMessage>
                        </div>

                        <div className="space-y-2">
                          <FormLabel className="text-sm">Dutch</FormLabel>
                          <Input
                            {...register(`attributes.${index}.reason_nl`)}
                          />
                          <FormMessage>
                            {errors.attributes?.[index]?.reason_nl?.message}
                          </FormMessage>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAttr(index)}
                      >
                        Remove Attribute
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={() =>
                  appendAttr({
                    credential_attribute_name: "",
                    reason_en: "",
                    reason_nl: "",
                  })
                }
              >
                Add Attribute
              </Button>
            </div>

            <div className="space-y-2 mt-4">
              <Button type="submit" disabled={isSaving}>
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
