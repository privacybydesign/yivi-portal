"use client";

import { useActionState, useEffect } from "react";
import { useRouter } from "next/navigation";
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
  RelyingPartyFormState,
  RelyingPartyInputs,
} from "@/src/actions/manage-relying-party";
import { generateSlug } from "@/lib/utils";
import { useForm } from "react-hook-form";
import { RelyingParty } from "@/src/models/relying-party";
import { useFieldArray } from "react-hook-form";

const defaultFormInput: RelyingPartyInputs = {
  rp_slug: "",
  hostnames: [{ hostname: "" }],
  trust_model_env: "",
  context_description_en: "",
  context_description_nl: "",
  attributes: [],
};
import { updateRelyingParty } from "@/src/actions/manage-relying-party";

export default function ManageRelyingPartyInformationForm({
  relying_party,
}: {
  relying_party?: RelyingParty;
}) {
  if (relying_party) {
    defaultFormInput.rp_slug = relying_party.rp_slug ?? "";
    defaultFormInput.hostnames = relying_party.hostnames ?? [{ hostname: "" }];
    defaultFormInput.trust_model_env = relying_party.environment ?? "";
    defaultFormInput.context_description_en = "";
    defaultFormInput.context_description_nl = "";
    defaultFormInput.attributes = [];
  }

  const [formState, formSubmit, pending] = useActionState<
    RelyingPartyFormState,
    FormData
  >(relying_party ? updateRelyingParty : registerRelyingParty, {
    values: defaultFormInput,
    errors: {},
  });

  const router = useRouter();
  if (formState?.success && formState?.redirectTo) {
    router.push(formState.redirectTo);
  }

  const form = useForm<RelyingPartyInputs>({
    defaultValues: defaultFormInput,
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "attributes",
  });

  useEffect(() => {
    form.clearErrors();

    if (formState?.errors) {
      Object.entries(formState.errors).forEach(([field, error]) => {
        if (error?.message) {
          form.setError(field as keyof RelyingPartyInputs, {
            type: "server",
            message: error.message,
          });
        }
      });
    }
  }, [formState?.errors, form]);

  const {
    fields: hostnameFields,
    append: appendHostname,
    remove: removeHostname,
  } = useFieldArray({
    control: form.control,
    name: "hostnames",
  });

  return (
    <Form {...form}>
      <form action={formSubmit} className="space-y-4">
        <FormField
          control={form.control}
          name="rp_slug"
          render={({ field: { onBlur, ...field } }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>Slug</Label>
                <FormDescription>
                  Slug you want to use for this relying party. This must be
                  different than your other relying parties.
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
          name="trust_model_env"
          render={({ field }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>Trust Model Environment</Label>
                <FormDescription>Select the environment.</FormDescription>
              </div>
              <div>
                <FormControl>
                  <select {...field} className="input">
                    <option value=" ">Select environment</option>
                    <option value="production">Production</option>
                    <option value="staging">Staging</option>
                    <option value="demo">Demo</option>
                  </select>
                </FormControl>
              </div>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="context_description_en"
          render={({ field }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>Context Description (EN)</Label>
                <FormDescription>English context description.</FormDescription>
              </div>
              <div>
                <FormControl>
                  <Input {...field} />
                </FormControl>
              </div>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="context_description_nl"
          render={({ field }) => (
            <FormItem className="grid md:grid-cols-2 items-start md:gap-4">
              <div className="py-1">
                <Label>Context Description (NL)</Label>
                <FormDescription>Dutch context description.</FormDescription>
              </div>
              <div>
                <FormControl>
                  <Input {...field} />
                </FormControl>
              </div>
            </FormItem>
          )}
        />
        <div className="space-y-4">
          <Label>Hostnames</Label>
          {hostnameFields.map((field, index) => (
            <FormField
              key={field.id}
              control={form.control}
              name={`hostnames.${index}.hostname`}
              render={({ field }) => (
                <FormItem className="flex items-center gap-2">
                  <FormControl>
                    <Input {...field} placeholder={`Hostname ${index + 1}`} />
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
            onClick={() => appendHostname({ hostname: "" })}
          >
            Add Hostname
          </Button>
        </div>

        <div className="space-y-6">
          {fields.map((field, index) => (
            <div
              key={field.id}
              className="grid grid-cols-1 md:grid-cols-2 gap-4 border p-4 rounded-md"
            >
              <FormField
                control={form.control}
                name={`attributes.${index}.credential_attribute_tag`}
                render={({ field }) => (
                  <FormItem>
                    <Label>Attribute Tag</Label>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name={`attributes.${index}.credential_attribute_name`}
                render={({ field }) => (
                  <FormItem>
                    <Label>Attribute Name</Label>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name={`attributes.${index}.reason_en`}
                render={({ field }) => (
                  <FormItem>
                    <Label>Reason (EN)</Label>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name={`attributes.${index}.reason_nl`}
                render={({ field }) => (
                  <FormItem>
                    <Label>Reason (NL)</Label>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <div className="col-span-2">
                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => remove(index)}
                >
                  Remove Attribute
                </Button>
              </div>
            </div>
          ))}

          <Button
            type="button"
            onClick={() =>
              append({
                credential_attribute_tag: "",
                credential_attribute_name: "",
                reason_en: "",
                reason_nl: "",
              })
            }
          >
            Add Attribute
          </Button>
        </div>

        <Button type="submit" disabled={pending} className="col-span-2">
          {pending ? "Submitting..." : "Submit"}
        </Button>

        {formState?.globalError && (
          <div className="col-span-2 text-sm text-red-600 font-medium">
            {formState.globalError}
          </div>
        )}
      </form>
    </Form>
  );
}
