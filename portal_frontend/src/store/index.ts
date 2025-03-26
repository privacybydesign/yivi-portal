"use client";

import { create } from 'zustand'
import { jwtDecode } from "jwt-decode";
import { useEffect } from "react";

interface StateStore {
    accessToken: string | null
    email: string | null
    role?: "admin" | "maintainer";
    organizationId?: string;
    setAccessToken: (accessToken: string | null) => void
    initializeAuth: () => void;
}

const useStore = create<StateStore>((set) => ({
    accessToken: null,
    email: null,
    role: undefined,
    organizationId: undefined,

    setAccessToken: (newToken: string | null) => {
        console.log(newToken);
        if (newToken) {
            const decoded = jwtDecode<AuthToken>(newToken);
            set({ email: decoded.email, role: decoded.role });
            localStorage.setItem("accessToken", newToken);
        } else {
            set({ email: null, role: undefined });
            localStorage.removeItem("accessToken");
        }
        set({ accessToken: newToken });
    },

    initializeAuth: () => {
        const savedAccessToken = localStorage.getItem("accessToken");
        if (savedAccessToken) {
            const decoded = jwtDecode<AuthToken>(savedAccessToken);
            const currentTime = Math.floor(Date.now() / 1000);

            if (decoded.exp < currentTime) {
                localStorage.removeItem("accessToken");
                set({ accessToken: null, email: null, role: undefined });
            } else {
                set({
                    accessToken: savedAccessToken,
                    email: decoded.email,
                    role: decoded.role,
                    organizationId: decoded.organizationId
                });
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