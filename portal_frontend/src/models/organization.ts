export interface Organization {
  id: string;
  name_en: string;
  name_nl: string;
  slug: string;
  registration_number: string;
  street: string;
  house_number: string;
  postal_code: string;
  country: string;
  city: string;
  is_verified: boolean;
  verified_at: string | null;
  logo: string;
  created_at: string;
  last_updated_at: string;
  is_RP: boolean;
  is_AP: boolean;
  trust_model: string;
}
