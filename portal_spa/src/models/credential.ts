export interface CredentialAttribute {
  id: number;
  credential_attribute_id: string;
  name_en: string;
  name_nl: string;
  full_path: string;
  description_en: string;
}

export interface Credential {
  id: number;
  name_en: string;
  name_nl: string;
  ap_slug: string;
  environment: string;
  org_name: string;
  org_slug: string;
  credential_id: string;
  description_en: string;
  attributes: CredentialAttribute[];
  full_path: string;
  issue_url: string;
  scheme_url: string; // TODO: Might be nice to add these later?
}
