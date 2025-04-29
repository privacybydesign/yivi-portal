import type { AppProps } from "next/app";
import { Geist, Geist_Mono } from "next/font/google";
import "@/src/styles/globals.css";
import { ReactElement, ReactNode } from "react";
import { NextPage } from 'next';
import { Toaster } from '@/src/components/ui/toaster';
import Header from '@/src/components/layout/app/header';

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
  // Use the layout defined at the page level, if available
  const getLayout = Component.getLayout ?? ((page) => page);

  return (
    <div className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
      <Header />

      {getLayout(<Component {...pageProps} />)}

      <Toaster />
    </div>
  );
}
