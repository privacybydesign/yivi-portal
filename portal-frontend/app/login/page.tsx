"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { Label } from "@/components/ui/label";
import { warnOptionHasBeenDeprecated } from "next/dist/server/config";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    import("@privacybydesign/yivi-frontend").then((yivi: any) => {
      const web = yivi.newWeb({
        debugging: false,            // Enable to get helpful output in the browser console
        element: '#yivi-web-form', // Which DOM element to render to
        language: 'en',             // Language to use
        // Back-end options
        session: {
          // Point this to your IRMA server:
          url: 'https://is.staging.yivi.app',

          start: {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              '@context': 'https://irma.app/ld/request/disclosure/v2',
              'disclose': [
                [
                  ['pbdf.pbdf.email.email'],
                  ['pbdf.sidn-pbdf.email.email'],
                ]
              ]
            })
          }
        }
      });
      web.start()
        .then(() => {
          alert('fine');
        })
        .catch((err: any) => {
          alert(err);
        });
    });
  }, []);

  const handleLogin = async () => {
    // Replace with actual authentication logic
    if (email === "admin@example.com" && password === "password") {
      router.push("/dashboard");
    } else {
      setError("Invalid credentials. Please try again.");
    }
  };

  return (
    <div className="flex justify-center items-center">
      <div className="flex grow p-6 justify-center items-center">
        <div id="yivi-web-form">
        </div>
      </div>
    </div>
  );
}