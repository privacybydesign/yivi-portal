"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <Image
          className="dark:invert"
          src="/yivi-logo.svg"
          alt="Yivi logo"
          width={180}
          height={38}
          priority
        />
        <h1 className="text-2xl sm:text-4xl font-bold text-center sm:text-left">
          Welcome to the Yivi Portal
        </h1>
        <p className="text-sm sm:text-base text-center sm:text-left">
          This is the Yivi portal where organizations can work together to create a secure and trusted ecosystem. Join us as a verifier, issuer, and become part of the Yivi ecosystem.
        </p>
        <ol className="list-inside list-decimal text-sm text-center sm:text-left font-[family-name:var(--font-geist-mono)]">
          <li className="mb-2">
            <strong>Become a Verifier:</strong> Verify the authenticity of credentials and ensure trust within the ecosystem.
          </li>
          <li className="mb-2">
            <strong>Become an Issuer:</strong> Issue credentials to users and organizations, contributing to a secure and reliable network.
          </li>
          <li className="mb-2">
            <strong>Join the Yivi Ecosystem:</strong> Collaborate with other organizations to build a robust and trusted environment.
          </li>
        </ol>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <a
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5"
            href="/login"
            target="_blank"
            rel="noopener noreferrer"
          >
            Get started
          </a>
          <a
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:min-w-44"
            href="https://docs.yivi.app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn More
          </a>
        </div>
      </main>
    </div>
  );
}
