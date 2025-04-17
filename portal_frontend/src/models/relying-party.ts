export interface RelyingParty {
  rp_slug: string;
  environment: string;
  hostnames: { hostname: string }[];
  published_at: string | null;
  status?: string;
  context_description_en?: string;
  context_description_nl?: string;
  attributes: {
    credential_attribute_name: string;
    reason_en: string;
    reason_nl: string;
  }[];
  approved_rp_details?: {
    hostnames: string[];
    id: string;
    scheme: string;
  };
  published_rp_details?: object;
  last_updated_at?: string;
  yivi_tme?: string;
}
