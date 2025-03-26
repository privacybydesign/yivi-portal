export interface Organization {
    id: string;
    name_en: string;
    name_nl: string;
    slug: string;
    registration_number: string;
    address: string;
    is_verified: boolean;
    verified_at: string | null;
    trade_names: string[];
    logo: string;
    created_at: string;
    last_updated_at: string;
    is_RP: boolean;
    is_AP: boolean;
    trust_model: string;
}
