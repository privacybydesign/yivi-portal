import { create } from "zustand";
import { jwtDecode } from "jwt-decode";
import { useEffect } from "react";
import type { AuthToken } from "@/models/auth_token";
import { axiosInstance } from "../services/axiosInstance";
import { AxiosError } from "axios";

interface StateStore {
  accessToken: string | null;
  email: string | null;
  role?: "admin" | "maintainer" | undefined;
  organizationSlug?: string | undefined;
  initialized: boolean;
  setAccessToken: (accessToken: string | null) => void;
  initializeAuth: () => void;
  refreshToken: () => Promise<string | null>;
}

const useStore = create<StateStore>((set) => ({
  accessToken: null,
  email: null,
  role: undefined,
  organizationSlug: undefined,
  initialized: false,

  setAccessToken: (newToken: string | null) => {
    if (newToken) {
      const decoded = jwtDecode<AuthToken>(newToken);
      set({
        email: decoded.email,
        role: decoded.role,
        organizationSlug: decoded.organizationSlug,
      });
      localStorage.setItem("accessToken", newToken);
    } else {
      set({ email: null, role: undefined, organizationSlug: undefined });
      localStorage.removeItem("accessToken");
    }
    set({ accessToken: newToken });
  },

  refreshToken: async () => {
    try {
      const response = await axiosInstance.post<{ access: string }>(
        "/v1/refreshtoken"
      );
      if (response.status !== 200) {
        return null;
      }

      const newToken = response.data.access;
      if (newToken) {
        const newDecoded = jwtDecode<AuthToken>(newToken);
        set({
          accessToken: newToken,
          email: newDecoded.email,
          role: newDecoded.role,
          organizationSlug: newDecoded.organizationSlug,
        });
        localStorage.setItem("accessToken", newToken);
        return newToken;
      }

      // Could not refresh — clear auth
      set({
        accessToken: null,
        email: null,
        role: undefined,
        organizationSlug: undefined,
      });
      localStorage.removeItem("accessToken");
    } catch (error: unknown) {
      if (error instanceof AxiosError) {
        console.warn("Error refreshing token:", error.response?.data.detail);
      } else {
        console.warn("Unexpected error", error);
      }
    }
    return null;
  },

  initializeAuth: () => {
    const savedAccessToken = localStorage.getItem("accessToken");
    if (savedAccessToken) {
      const decoded = jwtDecode<AuthToken>(savedAccessToken);
      const currentTime = Math.floor(Date.now() / 1000);

      if (decoded.exp < currentTime + 60) {
        // Try refreshing token
        useStore.getState().refreshToken();
      } else {
        set({
          accessToken: savedAccessToken,
          email: decoded.email,
          role: decoded.role,
          organizationSlug: decoded.organizationSlug,
          initialized: true,
        });
        return;
      }
    }

    // No valid token - clear
    set({
      accessToken: null,
      email: null,
      role: undefined,
      organizationSlug: undefined,
      initialized: true,
    });
  },
}));

// Hook to initialize authentication in a React component
export function useAuthInit() {
  const initializeAuth = useStore((state) => state.initializeAuth);
  const initialized = useStore((state) => state.initialized);

  useEffect(() => {
    if (!initialized) {
      initializeAuth();
    }
  }, [initializeAuth, initialized]);
}

export default useStore;
