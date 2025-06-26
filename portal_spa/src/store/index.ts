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
  organizationSlugs: string[];
  initialized: boolean;
  setAccessToken: (accessToken: string | null) => void;
  initializeAuth: () => void;
  refreshToken: (data?: unknown) => Promise<string | null>;
}

const useStore = create<StateStore>((set) => ({
  accessToken: null,
  email: null,
  role: undefined,
  organizationSlugs: [],
  initialized: false,

  setAccessToken: (accessToken: string | null) => {
    if (accessToken) {
      const decoded = jwtDecode<AuthToken>(accessToken);

      set({
        email: decoded.email,
        role: decoded.role,
        organizationSlugs: decoded.organizationSlugs || [],
      });
      localStorage.setItem("accessToken", accessToken);
    } else {
      set({ email: null, role: undefined, organizationSlugs: [] });
      localStorage.removeItem("accessToken");
    }

    set({ accessToken });
  },

  refreshToken: async (data?: unknown) => {
    try {
      const response = await axiosInstance.post<{ access: string }>(
        "/v1/refreshtoken",
        data
      );

      if (response.status !== 200) {
        return null;
      }

      useStore.getState().setAccessToken(response.data.access);
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
          organizationSlugs: decoded.organizationSlugs || [],
          initialized: true,
        });
      }
    } else {
      // No valid token - clear
      set({
        accessToken: null,
        email: null,
        role: undefined,
        organizationSlugs: [],
        initialized: true,
      });
    }
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

export function useIdleRefresh() {
  const accessToken = useStore((state) => state.accessToken);
  const refreshToken = useStore((state) => state.refreshToken);

  let pageUnloaded = false;
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      pageUnloaded = true;
    } else if (pageUnloaded && accessToken) {
      const decoded = jwtDecode<AuthToken>(accessToken);
      const currentTime = Math.floor(Date.now() / 1000);
      if (decoded.exp < currentTime + 60) {
        refreshToken();
      }
      pageUnloaded = false;
    }
  });
}

export default useStore;
