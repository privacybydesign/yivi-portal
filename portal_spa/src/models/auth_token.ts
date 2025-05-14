export interface AuthToken {
  token_type: "access" | "refresh"; // Assuming "access" and "refresh" as possible values
  exp: number; // Expiration time (Unix timestamp)
  iat: number; // Issued at time (Unix timestamp)
  jti: string; // Unique identifier for the token
  user_id: string; // User identifier (could be an email or a UUID)
  email: string; // User email
  role?: "admin" | "maintainer" | undefined; // User role (e.g., "user", "admin")
  organizationSlugs?: string[]; // Organization identifier
}
