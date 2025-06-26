import type { Credential } from "@/models/credential";

export type SearchOptions = {
  query: string;
  credentials: Credential[];
  environmentWeights?: Record<string, number>;
  filterByEnv?: Record<string, boolean>;
};

export function filterAndRankCredentials({
  query,
  credentials,
  environmentWeights = { production: 1, staging: 0.8, demo: 0.5 },
  filterByEnv,
}: SearchOptions): Credential[] {
  const q = query.toLowerCase().trim();

  const shouldFilterEnv = !!filterByEnv;

  const scored = credentials
    .map((cred) => {
      if (shouldFilterEnv && !filterByEnv?.[cred.environment]) return null;

      let score = 0;
      const credMatch = cred.name_en?.toLowerCase() === q;
      const nameMatch = cred.name_en?.toLowerCase().includes(q);
      const attributeMatch = cred.attributes?.some((attr) =>
        attr.name_en?.toLowerCase().includes(q)
      );

      if (credMatch) score += 2;
      if (nameMatch) score += 1;
      if (attributeMatch) score += 0.5;

      score *= environmentWeights[cred.environment] ?? 1;

      let bucket = 3;
      if (cred.deprecated_since) {
        bucket = 4;
      } else if (credMatch) {
        bucket = 0;
      } else if (nameMatch) {
        bucket = 1;
      } else if (attributeMatch) {
        bucket = 2;
      }

      return { cred, score, bucket };
    })
    .filter(
      (item): item is { cred: Credential; score: number; bucket: number } =>
        !!item
    )
    .filter((item) => q === "" || item.score > 0 || item.cred.deprecated_since)
    .sort((a, b) => {
      if (q === "") {
        return a.cred.name_en.localeCompare(b.cred.name_en, undefined, {
          sensitivity: "base",
        });
      }
      if (a.bucket !== b.bucket) return a.bucket - b.bucket;
      return b.score - a.score;
    })
    .map((item) => item.cred);

  return scored;
}
