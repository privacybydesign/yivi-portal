export function getLocalizedField(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  obj: any,
  key: string,
  lang: string
): string {
  if (lang === "nl" && obj[`${key}_nl`]) return obj[`${key}_nl`];
  if (lang === "en" && obj[`${key}_en`]) return obj[`${key}_en`];
  return obj[`${key}_en`] || obj[`${key}_nl`] || "";
}
