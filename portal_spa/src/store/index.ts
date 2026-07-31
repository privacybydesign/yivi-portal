import { create } from "zustand";
import { jwtDecode } from "jwt-decode";
import { useEffect } from "react";
import type { AuthToken } from "@/models/auth_token";
import { axiosInstance } from "../services/axiosInstance";
import { isAxiosError } from "axios";

let refreshInProgress: Promise<string | null> | null = null;

const decodeToken = (token: string): AuthToken | null => {
  try {
    return jwtDecode<AuthToken>(token);
  } catch {
    return null;
  }
};

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
        if (isAxiosError(error) && error.response?.status === 401) {
          // The session is gone (expired or never existed). Drop the stale
          // token so we stop retrying on every request and every page load.
          useStore.getState().setAccessToken(null);
        } else if (isAxiosError(error)) {
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
    const decoded = savedAccessToken ? decodeToken(savedAccessToken) : null;

    if (savedAccessToken && !decoded) {
      // Unreadable token - drop it instead of letting it fail on every call.
      localStorage.removeItem("accessToken");
    }

    if (decoded) {
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
        const decoded = decodeToken(accessToken);

        if (decoded && decoded.exp < currentTime + 60) {
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
