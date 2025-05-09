import axios from "axios";
import { jwtDecode } from "jwt-decode";
import useStore from "@/store";
import type { AuthToken } from "@/models/auth_token";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_ENDPOINT ?? "%VITE_API_ENDPOINT%",
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
  let token = accessToken;

  if (!token || isTokenExpiring(token)) {
    token = await refreshToken();
  }

  return token;
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
  (error) => Promise.reject(error)
);
