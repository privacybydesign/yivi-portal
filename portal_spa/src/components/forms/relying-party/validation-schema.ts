import { z } from "zod";

export const RelyingPartySchema = z.object({
  rp_slug: z
    .string()
    .min(2, "Slug is too short")
    .regex(/^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*$/, {
      message:
        "Slug must start with a letter, can contain letters, digits, and hyphens.",
    }),

  context_description_en: z
    .string()
    .nonempty("English context description is required"),
  context_description_nl: z
    .string()
    .nonempty("Dutch context description is required"),

  hostnames: z.array(
    z.object({
      hostname: z
        .string()
        .regex(
          /^(?=^.{1,253}$)(([a-z\d]([a-z\d-]{0,62}[a-z\d])*[\.]){1,3}[a-z]{1,61})$/gm,
          "Hostname must be a valid domain (e.g. example.com, sub.domain.dev)"
        ),
      id: z.number().optional(),
    })
  ),

  attributes: z
    .array(
      z.object({
        credential_id: z
          .number({ invalid_type_error: "Credential is required" })
          .int("Credential ID must be a number"),
        credential_attribute_tag: z
          .string()
          .nonempty("Credential attribute is required"),
        reason_en: z.string().nonempty("English reason is required"),
        reason_nl: z.string().nonempty("Dutch reason is required"),
      })
    )
    .min(1, "At least one attribute is required"),
  ready: z.boolean(),
});

export type RelyingPartyFormData = z.infer<typeof RelyingPartySchema>;
