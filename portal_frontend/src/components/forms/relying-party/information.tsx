"use client";

import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { RelyingPartySchema, RelyingPartyFormData } from "./validation-schema";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../../ui/form";
import { Input } from "../../ui/input";
import { Textarea } from "../../ui/textarea";
import { Button } from "../../ui/button";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "../../ui/select";
import { useEffect, useState } from "react";
import DnsChallenges from "@/src/components/forms/relying-party/dnscheck";

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
      globalError?: string;
      isSaving: boolean;
      onClose?: () => void;
    }
  | {
      isEditMode: false;
      originalSlug?: never; // ✅ Enforce that it can't be passed
      defaultValues: RelyingPartyFormData;
      onSubmit: (data: RelyingPartyFormData) => void;
      serverErrors?: Partial<Record<keyof RelyingPartyFormData, string>>;
      globalError?: string;
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
  const { toast } = useToast();

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
      toast({
        title: "Error",
        description: globalError,
        variant: "destructive",
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
              if (isEditMode) {
                const payload = getChangedFormData(defaultValues, formData);
                if (Object.keys(payload).length === 0) {
                  toast({
                    title: "No changes detected",
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
                  <FormMessage>{serverErrors.environment}</FormMessage>
                </FormItem>
              )}
            />

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

              <div className="space-y-2  p-1 rounded-md">
                {hostnameFields.map((field, index) => (
                  <div key={field.id} className="flex gap-2 items-start">
                    <Input
                      {...register(`hostnames.${index}.hostname`)}
                      defaultValue={field.hostname} // ✅ Use string directly
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
                    <div>
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

                    <div>
                      <FormLabel className="font-medium">Reason</FormLabel>
                      <div className="grid md:grid-cols-2 gap-4 mt-2">
                        <div>
                          <FormLabel className="text-sm">English</FormLabel>
                          <Input
                            {...register(`attributes.${index}.reason_en`)}
                          />
                          <FormMessage>
                            {errors.attributes?.[index]?.reason_en?.message}
                          </FormMessage>
                        </div>

                        <div>
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

                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeAttr(index)}
                    >
                      Remove Attribute
                    </Button>
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
