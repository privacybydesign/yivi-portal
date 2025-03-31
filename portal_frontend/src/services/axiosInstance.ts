import axios from 'axios';
import getConfig from 'next/config';
import useStore from '../store';
const { publicRuntimeConfig } = getConfig();

export const axiosInstance = axios.create({
  baseURL: publicRuntimeConfig.API_ENDPOINT,
});

axiosInstance.interceptors.request.use(
  (config) => {
    // Access token directly from Zustand store
    const { accessToken } = useStore.getState();

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);