import { create } from 'zustand'
import { jwtDecode } from "jwt-decode";

export interface Organization {
    id: string;
    name: string;
    domain: string;
    logo: string;
    issuer: {
      status: string;
      color: string;
    };
    verifier: {
      status: string;
      color: string;
    };
  }
  

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

const useStore = create<StateStore>((set, get) => {
    const savedAccessToken = localStorage.getItem('accessToken');
    let initialEmail = null;
    let initialRole = null;
    let isTokenExpired = false;

    if (savedAccessToken) {
        const decoded = jwtDecode<AuthToken>(savedAccessToken);
        const currentTime = Math.floor(Date.now() / 1000);

        if (decoded.exp < currentTime) {
            localStorage.removeItem('accessToken');
            isTokenExpired = true;
        } else {
            initialEmail = decoded.email;
            initialRole = decoded.role;
        }
    }

    return {
        accessToken: isTokenExpired ? null : savedAccessToken,
        email: initialEmail,
        role: initialRole,
        setAccessToken: (accessToken: string | null) => {
            if (accessToken) {
                const decoded = jwtDecode<AuthToken>(accessToken);
                decoded.email && set({ email: decoded.email });
                decoded.role && set({ role: decoded.role });
                localStorage.setItem('accessToken', accessToken);
            } else {
                set({ email: null });
                set({ role: null });
                localStorage.removeItem('accessToken');
            }
            set({ accessToken });
        },
    };
});

export default useStore;