export interface RelyingParty {
  rp_slug: string;
  environment: string;
  hostnames: { hostname: string }[];
  published_at: string | null;
  status?: string;
  approved_rp_details?: {
    hostnames: string[];
    id: string;
    scheme: string;
  };
  published_rp_details?: object;
  last_updated_at?: string;
  yivi_tme?: string;
}
