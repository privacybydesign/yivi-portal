export interface CredentialAttribute {
  id: number;
  credential_attribute_id: string;
  name_en: string;
  name_nl: string;
  full_path: string;
}

export interface Credential {
  id: number;
  name_en: string;
  credential_id: string;
  description: string;
  attributes: CredentialAttribute[];
  full_path: string;
}
