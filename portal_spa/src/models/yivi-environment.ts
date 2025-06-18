export type YiviEnvironment = {
  id: number;
  environment: Environment;
  name_en: string;
  name_nl: string;
  description_en: string;
  description_nl: string;
  url: string;
  scheme_id: string;
  timestamp_server: string;
  keyshare_server: string;
  keyshare_website: string;
  keyshare_attribute: string;
  contact_website: string;
};

export enum Environment {
  production = "production",
  staging = "staging",
  demo = "demo",
}
