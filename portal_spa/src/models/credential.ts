import type { Environment } from "./yivi-environment";

export interface CredentialAttribute {
  id?: number;
  credential_attribute_tag: string;
  name_en?: string;
  name_nl?: string;
  reason_en: string;
  reason_nl: string;
  full_path?: string;
  description_en?: string;
  credential_id: number;
}

export interface Credential {
  id: number;
  name_en: string;
  name_nl: string;
  ap_slug: string;
  environment: Environment;
  org_name: string;
  org_slug: string;
  credential_id: string;
  description_en: string;
  attributes: CredentialAttribute[];
  full_path: string;
  issue_url: string;
  deprecated_since?: string;
}
