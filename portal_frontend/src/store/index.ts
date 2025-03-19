"use client";

import { create } from 'zustand'
import { jwtDecode } from "jwt-decode";
import { useEffect } from "react";

export interface Organization {
    id: string;
    name_en: string;
    name_nl: string;
    slug: string;
    registration_number: string;
    address: string;
    is_verified: boolean;
    verified_at: string | null;
    trade_names: string[];
    logo: string;
    created_at: string;
    last_updated_at: string;
    is_RP: boolean;
    is_AP: boolean;
    trust_model: string | null;
}

export interface PaninatedResult<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
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
    setAccessToken: (accessToken: string | null) => void
    initializeAuth: () => void;
}

const useStore = create<StateStore>((set) => ({
    accessToken: null,
    email: null,
    role: null,

    setAccessToken: (newToken: string | null) => {
        if (typeof window !== "undefined") { // ✅ Ensure this runs in the browser
            console.log(newToken);
            if (newToken) {
                const decoded = jwtDecode<AuthToken>(newToken);
                set({ email: decoded.email, role: decoded.role });
                localStorage.setItem("accessToken", newToken);
            } else {
                set({ email: null, role: null });
                localStorage.removeItem("accessToken");
            }
            set({ accessToken: newToken });
        }
    },

    initializeAuth: () => {
        if (typeof window !== "undefined") { // ✅ Ensure this runs in the browser
            const savedAccessToken = localStorage.getItem("accessToken");
            if (savedAccessToken) {
                const decoded = jwtDecode<AuthToken>(savedAccessToken);
                const currentTime = Math.floor(Date.now() / 1000);
                
                if (decoded.exp < currentTime) {
                    localStorage.removeItem("accessToken");
                    set({ accessToken: null, email: null, role: null });
                } else {
                    set({ accessToken: savedAccessToken, email: decoded.email, role: decoded.role });
                }
            }
        }
    },
}));

// Hook to initialize authentication in a React component
export function useAuthInit() {
    const initializeAuth = useStore((state) => state.initializeAuth);

    useEffect(() => {
        initializeAuth();
    }, [initializeAuth]);
}

export default useStore;