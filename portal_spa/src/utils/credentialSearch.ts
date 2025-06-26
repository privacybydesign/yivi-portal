import type { Credential } from "@/models/credential";
import { scoreCredentials } from "./scoreCredentials";

export type SearchOptions = {
  searchQuery: string;
  credentials: Credential[];
  environmentWeights?: Record<string, number>;
  selectedEnv?: Record<string, boolean>;
};

const filterByEnvironment = (
  // Check whether to include a credential based on the selected environment
  cred: Credential,
  selectedEnv?: Record<string, boolean>
): boolean => {
  if (!selectedEnv) return true;
  return selectedEnv[cred.environment] ?? false;
};

export function filterAndRankCredentials({
  searchQuery,
  credentials,
  selectedEnv, // e.g. {"production": true, "staging": true, "demo": true}
}: SearchOptions): Credential[] {
  const environmentWeights = { production: 1, staging: 0.8, demo: 0.5 };
  const query = searchQuery.toLowerCase().trim();

  const filtered = credentials
    .filter((cred) => filterByEnvironment(cred, selectedEnv))
    .filter((cred) => !cred.deprecated_since);

  const scored = filtered
    .map((cred) => scoreCredentials(cred, environmentWeights, query))
    .filter((item) => item.score > 0);

  scored.sort((a, b) => {
    return b.score - a.score;
  });

  const result = scored.map((item) => item.cred);

  return result;
}
