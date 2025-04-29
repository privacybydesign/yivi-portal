"use client";

import { create } from "zustand";
import { jwtDecode } from "jwt-decode";
import { useEffect } from "react";
import { AuthToken } from "@/src/models/auth_token";
import { axiosInstance } from "../services/axiosInstance";

interface StateStore {
  accessToken: string | null;
  email: string | null;
  role?: "admin" | "maintainer";
  organizationId?: string;
  setAccessToken: (accessToken: string | null) => void;
  initializeAuth: () => void;
  refreshToken: () => Promise<string | null>;
}

const useStore = create<StateStore>((set) => ({
  accessToken: null,
  email: null,
  role: undefined,
  organizationId: undefined,

  setAccessToken: (newToken: string | null) => {
    if (newToken) {
      const decoded = jwtDecode<AuthToken>(newToken);
      set({
        email: decoded.email,
        role: decoded.role,
        organizationId: decoded.organizationId
      });
      localStorage.setItem("accessToken", newToken);
    } else {
      set({ email: null, role: undefined, organizationId: undefined });
      localStorage.removeItem("accessToken");
    }
    set({ accessToken: newToken });
  },

  refreshToken: async () => {
    const response = await axiosInstance.post<{ access: string; }>('/v1/refreshtoken');
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
        organizationId: newDecoded.organizationId,
      });
      localStorage.setItem("accessToken", newToken);
      return newToken;
    } else {
      // Could not refresh — clear auth
      set({ accessToken: null, email: null, role: undefined, organizationId: undefined });
      localStorage.removeItem("accessToken");
    }
    return null;
  },

  initializeAuth: async () => {
    const savedAccessToken = localStorage.getItem("accessToken");
    if (savedAccessToken) {
      const decoded = jwtDecode<AuthToken>(savedAccessToken);
      const currentTime = Math.floor(Date.now() / 1000);

      if (decoded.exp < (currentTime + 60)) {
        // Try refreshing token
        await useStore.getState().refreshToken();

      } else {
        set({
          accessToken: savedAccessToken,
          email: decoded.email,
          role: decoded.role,
          organizationId: decoded.organizationId,
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
