"use client";

import Image from "next/image";
import { Button } from "../components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import Link from "next/link";

export default function Home() {
  console.log(process.env.NEXT_PUBLIC_API_ENDPOINT);
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
          Explore the Yivi ecosystem and discover how you can participate.
        </p>
        
        <div className="grid gap-4 sm:grid-cols-2 w-full max-w-2xl">
          <Card>
            <CardHeader>
              <CardTitle>I am a Yivi user, where can I use Yivi?</CardTitle>
            </CardHeader>
            <CardContent>
              Find out where you can authenticate using Yivi.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link href="/organizations">Explore relying parties</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>I want to become a relying party.</CardTitle>
            </CardHeader>
            <CardContent>
              Integrate Yivi authentication into your services.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link href="/organizations">Register relying party</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>I want to become an attestation provider.</CardTitle>
            </CardHeader>
            <CardContent>
              Issue credentials for the Yivi ecosystem.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link href="/organizations">Register attestation provider</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>I want to manage my organization.</CardTitle>
            </CardHeader>
            <CardContent>
              Administer your organization’s role in the Yivi ecosystem.
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link href="/manage-organization">Manage organization</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
