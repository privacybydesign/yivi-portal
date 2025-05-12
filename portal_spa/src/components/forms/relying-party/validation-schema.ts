import { z } from "zod";

export const RelyingPartySchema = z.object({
  rp_slug: z
    .string()
    .min(2, "Slug is too short")
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, {
      message: "Slug must be lowercase, hyphen-separated",
    }),

  environment: z.string().nonempty("Environment is required"),

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

  attributes: z.array(
    z.object({
      credential_attribute_name: z
        .string()
        .nonempty("Credential attribute name is required"),
      reason_en: z.string().nonempty("English reason is required"),
      reason_nl: z.string().nonempty("Dutch reason is required"),
    })
  ),
});

export type RelyingPartyFormData = z.infer<typeof RelyingPartySchema>;
