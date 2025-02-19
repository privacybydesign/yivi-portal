import { create } from 'zustand'
import { jwtDecode } from "jwt-decode";

interface AuthToken {
    token_type: "access" | "refresh"; // Assuming "access" and "refresh" as possible values
    exp: number; // Expiration time (Unix timestamp)
    iat: number; // Issued at time (Unix timestamp)
    jti: string; // Unique identifier for the token
    user_id: string; // User identifier (could be an email or a UUID)
    email: string; // User email
    role: string; // User role (e.g., "user", "admin")
    organizationId: string; // Organization identifier
}

interface StateStore {
    accessToken: string | null
    email: string | null
    role: string | null
    setAccessToken: (accessToken: string) => void
}

const useStore = create<StateStore>((set, get) => ({
    accessToken: null,
    email: null,
    role: null,
    setAccessToken: (accessToken: string) => {
        const decoded = jwtDecode<AuthToken>(accessToken)
        decoded.email && set({ email: decoded.email })
        decoded.role && set({ role: decoded.role })
        set({ accessToken })
    },
}));

export default useStore;