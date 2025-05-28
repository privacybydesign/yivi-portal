import type { Credential } from "@/models/credential";
export interface AttestationProvider {
  ap_slug: string;
  environment: string;
  last_updated_at: string;
  created_at: string;
  published: boolean;
  published_at: string | null;
  status?: string;
  ready: boolean;
  contact_email: string;
  contact_address: string;
  credentials: Credential[];
  organization: string;
  yivi_tme: string;
  full_path: string;
  organization_logo: string;
}
