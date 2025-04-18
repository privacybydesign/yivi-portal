import type { AppProps } from "next/app";
import { Geist, Geist_Mono } from "next/font/google";
import "../styles/globals.css";
import { ReactElement, ReactNode, useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import useStore from "@/src/store";
import { useRouter } from "next/navigation";
import { initials } from "@dicebear/collection";
import { createAvatar } from "@dicebear/core";
import { axiosInstance } from "../services/axiosInstance";
import { NextPage } from "next";
import { Toaster } from "@/src/components/ui/toaster";

export type NextPageWithLayout<P = object, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: ReactElement) => ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function MyApp({ Component, pageProps }: AppPropsWithLayout) {
  const initializeAuth = useStore((state) => state.initializeAuth);
  const router = useRouter();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Use the layout defined at the page level, if available
  const getLayout = Component.getLayout ?? ((page) => page);

  const email = useStore((state) => state.email);
  const setAccessToken = useStore((state) => state.setAccessToken);
  const [isOpen, setIsOpen] = useState(false);

  const svg = createAvatar(initials, {
    seed: email ?? "default-user",
    radius: 50,
    backgroundColor: ["d1d4f9", "ffd5dc", "c0aede"],
  }).toString();

  const handleLogout = () => {
    axiosInstance.post("/v1/logout").then(() => {
      // Redirect to login page
      setAccessToken(null);
      router.push("/login");
    });
  };

  return (
    <div className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto flex justify-between items-center px-4 py-3">
          {/* Left: Logo and Brand */}
          <div className="flex items-center gap-4">
            <Image
              src="/yivi-logo.svg"
              alt="Yivi Logo"
              height={32}
              width={54}
            />
            <Link href="/" className="text-xl font-semibold">
              Portal
            </Link>
          </div>

          {/* Center + Right: Nav and User Info */}
          <div className="hidden md:flex items-center gap-6">
            <Link href="/organizations" className="hover:text-blue-600 text-sm">
              Organizations
            </Link>

            {email ? (
              <div className="flex items-center gap-3 px-4 py-1 rounded-xl backdrop-blur-md bg-white/30 border border-white/50 shadow-sm">
                <Image
                  src={`data:image/svg+xml;utf8,${encodeURIComponent(svg)}`}
                  alt="User Avatar"
                  width={32}
                  height={32}
                  className="rounded-full border border-white"
                />
                <span className="text-sm truncate max-w-[140px] text-black/80">
                  {email}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-blue-600 hover:underline transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link href="/login" className="text-sm hover:text-blue-600">
                Login
              </Link>
            )}
          </div>

          {/* Mobile menu toggle */}
          <div className="md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="text-sm p-2">
              {isOpen ? "Close" : "Menu"}
            </button>
          </div>
        </div>
      </header>

      {getLayout(<Component {...pageProps} />)}

      <Toaster />
    </div>
  );
}
