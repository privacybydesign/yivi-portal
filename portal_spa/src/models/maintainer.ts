// The shape crypto.randomUUID() returns; browser code, so not Node's type.
type UUID = `${string}-${string}-${string}-${string}-${string}`;

export interface Maintainer {
  id: string;
  email: string;
  role: string;
  organization: UUID;
  // first_name: string;
  // last_name: string;
}
