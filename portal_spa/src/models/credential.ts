export interface CredentialAttribute {
  id: number;
  credential_attribute_id: string;
  name_en: string;
  name_nl: string;
}

export interface Credential {
  id: number;
  name: string;
  credential_id: string;
  description: string;
  attributes: CredentialAttribute[];
  full_path: string;
}
