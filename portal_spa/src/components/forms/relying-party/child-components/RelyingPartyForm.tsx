import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { RelyingPartySchema } from "../validation-schema";
import type { RelyingPartyFormData } from "../validation-schema";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useEffect, useState } from "react";
import { fetchCredentials } from "@/actions/manage-relying-party";
import type { Credential } from "@/models/credential";

import ContextDescription from "./ContextDescription";
import Hostnames from "./Hostnames";
import { CredentialAttributes } from "./CredentialAttributes";
import ReadyCheckbox from "./ReadyCheckbox";
import RelyingPartySlug from "./RelyingPartySlug";
import { useRelyingParty } from "@/contexts/relying-party/RelyingPartyContext";

export default function RelyingPartyForm() {
  const context = useRelyingParty();

  const { originalSlug, defaultValues, isProcessing, isEditMode, onClose } =
    context;

  const form = useForm<RelyingPartyFormData>({
    resolver: zodResolver(RelyingPartySchema),
    defaultValues,
  });

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = form;

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
              context.onSubmit(payload, originalSlug);
            } else {
              context.onSubmit(formData);
            }
          })}
        >
          {/* Relying party slug  */}
          <RelyingPartySlug control={control} formErrors={errors} />

          {/* Hostnames */}
          <Hostnames control={control} />

          {/* Context Description */}
          <ContextDescription control={control} />

          {/* Credential Selection and Attributes */}
          <CredentialAttributes form={form} credentials={credentials} />

          <ReadyCheckbox control={control} />

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
                className="text-sm"
              >
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              disabled={isProcessing}
              className="h-9 px-4 text-sm"
            >
              {isEditMode
                ? isProcessing
                  ? "Saving..."
                  : "Save"
                : isProcessing
                ? "Creating..."
                : "Create"}
            </Button>
          </div>
        </form>
      </Form>
    </>
  );
}
