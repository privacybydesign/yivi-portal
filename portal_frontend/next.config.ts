import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone",
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000'
      },
    ],
  },
  publicRuntimeConfig: {
    API_ENDPOINT: process.env.NEXT_PUBLIC_API_ENDPOINT
  }
};

export default nextConfig;
