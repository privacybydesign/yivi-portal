import { z } from "zod";

export const RelyingPartySchema = z.object({
  rp_slug: z
    .string()
    .min(2, "Slug is too short")
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, {
      message: "Slug must be lowercase, hyphen-separated",
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
          /^(?!:\/\/)([a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,}$/,
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
