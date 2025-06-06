export interface Organization {
  id: string;
  name_en: string;
  name_nl: string;
  slug: string;
  street: string;
  house_number: string;
  postal_code: string;
  country: string;
  city: string;
  is_verified: boolean;
  logo: string;
  created_at: string;
  last_updated_at: string;
  is_RP: boolean;
  is_AP: boolean;
  trust_models?: trust_model[];
  verification_status: string;
}
export type trust_model = {
  name: string;
};
