interface RelyingParty {
    id: number;
    yivi_tme: string;
    organization: string;
    status: string | null;
    approved_rp_details: {
      id: string;
      logo: string;
      hostnames: string[];
      name: {
        en: string;
        nl: string;
      };
      scheme: string;
    };
    published_rp_details: {
      id: string;
      logo: string;
      hostnames: string[];
      name: {
        en: string;
        nl: string;
      };
      scheme: string;
    };
    created_at: string;
    last_updated_at: string;
  }