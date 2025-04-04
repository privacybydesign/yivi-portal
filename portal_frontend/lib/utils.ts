export function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}


export const generateSlug = (text: string) => {
  return text
    .toLowerCase()
    .replace(/\s+/g, "-")         // replace spaces with hyphen
    .replace(/[^a-z0-9-]/g, "");   // allow only lowercase letters, digits, and hyphen
};