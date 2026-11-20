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
  // Only serialized for a maintainer of this organization, or for an admin.
  contact_number?: string;
  contact_email?: string;
  // Where users of the Yivi app reach the organization's support. Public.
  support_email?: string | null;
  support_url?: string | null;
}
export type trust_model = {
  name: string;
};
