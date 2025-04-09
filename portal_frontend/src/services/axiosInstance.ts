import axios from "axios";
import getConfig from "next/config";
import useStore from "../store";
import Router from "next/router";
import { jwtDecode } from "jwt-decode";
import { AuthToken } from "@/src/models/auth_token";

const { publicRuntimeConfig } = getConfig();

export const axiosInstance = axios.create({
  baseURL: publicRuntimeConfig.API_ENDPOINT,
  withCredentials: true,
});

const isTokenExpiring = (token: string): boolean => {
  try {
    const { exp } = jwtDecode<AuthToken>(token);
    const currentTime = Math.floor(Date.now() / 1000);
    return exp < (currentTime + 60);
  } catch {
    return true; // invalid token
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

    if (!token) {
      Router.push("/login");
      return config;
    }

    config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);
