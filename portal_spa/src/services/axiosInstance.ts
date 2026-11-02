import axios from "axios";
import { jwtDecode } from "jwt-decode";
import useStore from "@/store";
import type { AuthToken } from "@/models/auth_token";

export const apiEndpoint =
  import.meta.env.VITE_API_ENDPOINT ?? "%VITE_API_ENDPOINT%";

export const axiosInstance = axios.create({
  baseURL: apiEndpoint,
  withCredentials: true,
});

const isTokenExpiring = (token: string): boolean => {
  try {
    const { exp } = jwtDecode<AuthToken>(token);
    const currentTime = Math.floor(Date.now() / 1000);
    return exp < currentTime + 60; // If expiring in 1 minute
  } catch {
    return true; // Invalid token
  }
};

const getValidAccessToken = async (): Promise<string | null> => {
  const { accessToken, refreshToken } = useStore.getState();

  // The access token is kept in memory only - there is no localStorage
  // fallback. On the very first request of a page load the store may still be
  // empty; there is nothing to send and a refresh would be a guaranteed 401 for
  // anonymous visitors, so the request goes out unauthenticated. The session of
  // a returning user is restored separately by initializeAuth() via the
  // HttpOnly refresh cookie.
  if (!accessToken) {
    return null;
  }

  if (!isTokenExpiring(accessToken)) {
    return accessToken;
  }

  return refreshToken();
};

axiosInstance.interceptors.request.use(
  async (config) => {
    if (config.url?.includes("/refreshtoken")) {
      return config; // Skip for refresh endpoint
    }

    const token = await getValidAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);
