import type { Credential } from "@/models/credential";
export const scoreCredentials = (
  cred: Credential,
  environmentWeights: Record<string, number>,
  searchQuery: string
): { cred: Credential; score: number } => {
  let score = 0;
  const credMatch = cred.name_en?.toLowerCase() === searchQuery;
  const nameMatch = cred.name_en?.toLowerCase().includes(searchQuery);
  const attributeMatch = cred.attributes?.some((attr) =>
    attr.name_en?.toLowerCase().includes(searchQuery)
  );

  if (credMatch) score += 2;
  if (nameMatch) score += 1;
  if (attributeMatch) score += 0.5;

  score *= environmentWeights[cred.environment] ?? 1;

  return { cred, score };
};
