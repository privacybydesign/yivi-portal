import { create } from "zustand";
import { jwtDecode } from "jwt-decode";
import { useEffect } from "react";
import type { AuthToken } from "@/models/auth_token";
import { axiosInstance } from "../services/axiosInstance";
import { AxiosError } from "axios";

let refreshInProgress: Promise<string | null> | null = null;

export interface StateStore {
  accessToken: string | null;
  email: string | null;
  role?: "admin" | "maintainer" | undefined;
  organizationSlugs: string[];
  initialized: boolean;
  setAccessToken: (accessToken: string | null) => void;
  initializeAuth: () => Promise<void>;
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
    if (refreshInProgress) {
      return refreshInProgress;
    }

    refreshInProgress = (async () => {
      try {
        const response = await axiosInstance.post<{ access: string }>(
          "/v1/refreshtoken",
          data,
        );

        if (response.status !== 200) {
          return null;
        }

        useStore.getState().setAccessToken(response.data.access);
        return response.data.access;
      } catch (error: unknown) {
        if (error instanceof AxiosError) {
          console.warn("Error refreshing token:", error.response?.data.detail);
        } else {
          console.warn("Unexpected error", error);
        }
        return null;
      } finally {
        refreshInProgress = null;
      }
    })();

    return refreshInProgress;
  },

  initializeAuth: async () => {
    const savedAccessToken = localStorage.getItem("accessToken");

    if (savedAccessToken) {
      const decoded = jwtDecode<AuthToken>(savedAccessToken);
      const currentTime = Math.floor(Date.now() / 1000);

      if (decoded.exp < currentTime + 60) {
        // Try refreshing token
        await useStore.getState().refreshToken();
      } else {
        set({
          accessToken: savedAccessToken,
          email: decoded.email,
          role: decoded.role,
          organizationSlugs: decoded.organizationSlugs || [],
        });
      }
    } else {
      // No valid token - clear
      set({
        accessToken: null,
        email: null,
        role: undefined,
        organizationSlugs: [],
      });
    }
    set({ initialized: true });
  },
}));

export function useIdleRefresh() {
  const accessToken = useStore((state) => state.accessToken);
  const refreshToken = useStore((state) => state.refreshToken);

  useEffect(() => {
    const handler = (event?: Event) => {
      if (
        (document.visibilityState === "visible" ||
          event?.type === "pageshow") &&
        accessToken
      ) {
        const currentTime = Math.floor(Date.now() / 1000);
        const decoded = jwtDecode<AuthToken>(accessToken);

        if (decoded.exp < currentTime + 60) {
          refreshToken();
        }
      }
    };
    document.addEventListener("visibilitychange", handler);
    window.addEventListener("pageshow", handler);

    handler(); // Run on first mount

    return () => {
      document.removeEventListener("visibilitychange", handler);
      window.removeEventListener("pageshow", handler);
    };
  }, [accessToken, refreshToken]);
}

export default useStore;
