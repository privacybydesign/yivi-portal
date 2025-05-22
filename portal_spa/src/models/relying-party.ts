export interface RelyingParty {
  rp_slug: string;
  environment: string;
  hostnames: {
    hostname: string;
    dns_challenge?: string;
    dns_challenge_created_at?: string;
    dns_challenge_verified?: boolean;
    dns_challenge_verified_at?: string;
    dns_challenge_invalidated_at?: string;
    manually_verified?: boolean;
  }[];
  last_updated_at: string;
  created_at: string;
  published: boolean;
  published_at: string | null;
  reviewed_at: string | null;
  status?: string;
  context_description_en?: string;
  context_description_nl?: string;
  attributes: {
    credential_id: number;
    credential_attribute_name: string;
    reason_en: string;
    reason_nl: string;
  }[];
}
