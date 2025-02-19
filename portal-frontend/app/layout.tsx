"use client";

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import useStore from "@/store";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const email = useStore((state) => state.email);
  const setAccessToken = useStore((state) => state.setAccessToken)
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    setAccessToken("");
    // Add any additional logout logic here
  };

  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <header className="bg-white shadow-md">
          <div className="container mx-auto flex justify-between items-center p-4">
            <Image src="/yivi-logo.svg" alt="Yivi Logo" height={30} width={54} />

            <div className="flex-1 pl-4">
              <Link href="/" className="text-xl">
                Portal
              </Link>
            </div>

            <nav className="hidden md:flex gap-6">
              <Link href="/organizations" className="hover:text-blue-600">
                Organizations
              </Link>
              {email ? (
                  <div className="flex items-center gap-4">
                  <span>{email}</span>
                  <button onClick={handleLogout} className="hover:text-blue-600">
                    Logout
                  </button>
                </div>
              ) : <Link href="/login" className="hover:text-blue-600">
                Login
              </Link>
              }
            </nav>

            <div className="md:hidden">
              <button onClick={() => setIsOpen(!isOpen)} className="p-2">
                {isOpen ? "Close" : "Menu"}
              </button>
            </div>
          </div>

          {isOpen && (
            <div className="md:hidden bg-white shadow-md absolute w-full left-0 top-0 h-screen flex flex-col items-center justify-center z-50">
              <Link href="/" className="block py-2 hover:text-blue-600">
                Home
              </Link>
              <Link href="/about" className="block py-2 hover:text-blue-600">
                About
              </Link>
              <Link href="/services" className="block py-2 hover:text-blue-600">
                Services
              </Link>
              <Link href="/extra" className="block py-2 hover:text-blue-600">
                Extra
              </Link>
            </div>
          )}
        </header>
        {children}
      </body>
    </html>
  );
}