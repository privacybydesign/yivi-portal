import { z } from "zod";

export const RelyingPartySchema = z.object({
  rp_slug: z
    .string()
    .min(2, "Slug is too short")
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, {
      message: "Slug must be lowercase, hyphen-separated",
    }),
  environment: z.string().min(1, "Environment is required"),
  context_description_en: z.string().min(1),
  context_description_nl: z.string().min(1),
  hostnames: z.array(
    z.object({
      hostname: z.string().url(),
    })
  ),
  attributes: z.array(
    z.object({
      credential_attribute_name: z.string(),
      reason_en: z.string(),
      reason_nl: z.string(),
    })
  ),
});

export type RelyingPartyFormData = z.infer<typeof RelyingPartySchema>;
