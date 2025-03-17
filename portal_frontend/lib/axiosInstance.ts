import axios from "axios";

// Create an Axios instance with custom settings
const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "https://your-api.com", // Set your API URL
  timeout: 10000, // Timeout after 10 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

// Optional: Add request interceptors
axiosInstance.interceptors.request.use(
  (config) => {
    // Example: Add auth token if available
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// // Optional: Add response interceptors
// axiosInstance.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     console.error("API Error:", error.response || error.message);
//     return Promise.reject(error);
//   }
// );

export default axiosInstance;
