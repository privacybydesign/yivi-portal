export interface CredentialAttribute {
  id: number;
  credential_attribute_id: string;
  name_en: string;
  name_nl: string;
}

export interface Credential {
  id: number;
  name_en: string;
  name_nl: string;
  credential_id: string;
  attributes: CredentialAttribute[];
}
