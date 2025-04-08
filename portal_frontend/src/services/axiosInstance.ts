// utils/api.js
import axios from "axios";
import getConfig from "next/config";
import useStore from "../store";
import Router from "next/router";

const { publicRuntimeConfig } = getConfig();

export const axiosInstance = axios.create({
  baseURL: publicRuntimeConfig.API_ENDPOINT,
});

axiosInstance.interceptors.request.use(
  (config) => {
    const { accessToken } = useStore.getState();

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    } else {
      Router.push("/access-denied");
    }

    config.headers.Authorization = `Bearer ${accessToken}`;
    return config;
  },
  (error) => Promise.reject(error)
);
