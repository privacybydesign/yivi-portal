/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";

import { apiEndpoint } from "@/services/axiosInstance";
import { newWeb, type YiviSession } from "@/services/yivi";
import useStore from "@/store";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function Login() {
  const setAccessToken = useStore((s) => s.setAccessToken);
  const navigate = useNavigate();
  const location = useLocation();
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const web: YiviSession = newWeb({
      debugging: import.meta.env.DEV,
      element: "#yivi-web-form",
      language: "en",
      minimal: true,
      session: {
        url: apiEndpoint + "/v1",
        start: {
          url: (o: any) => `${o.url}/session/`,
          method: "POST",
          credentials: "include",
        },
        result: {
          url: (o: any, { sessionToken }: any) =>
            `${o.url}/token/${sessionToken}`,
          method: "GET",
          credentials: "include",
        },
      },
    });

    web
      .start()
      .then((result: any) => {
        setAccessToken(result.access);
        if (location.state?.from) {
          navigate(location.state.from.pathname, { replace: true });
        } else {
          navigate(-1);
        }
      })
      .catch((err: unknown) => {
        if (err === "Cancelled" || err === "TimedOut" || err === "Error") {
          setAttempt((n) => n + 1);
        } else if (err !== "Aborted") {
          console.error("Yivi session error:", err);
        }
      });

    return () => {
      web.abort();
    };
  }, [navigate, setAccessToken, location, attempt]);

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-50 px-4 py-12">
      <Card className="w-full max-w-md border-slate-200 shadow-md">
        <CardHeader className="space-y-2 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-900 text-white">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <CardTitle className="text-2xl tracking-tight">
            Sign in to Yivi Portal
          </CardTitle>
          <CardDescription className="text-slate-600">
            Authenticate securely with your verified email credential.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="flex flex-col items-center">
            <div className="flex h-[272px] w-[272px] items-center justify-center rounded-lg border border-slate-200 bg-white p-4">
              <div
                id="yivi-web-form"
                data-testid="yivi-web-form"
                key={attempt}
              />
            </div>
          </div>

          <Separator className="my-6" />

          <ol className="space-y-3 text-sm text-slate-600">
            <Step n={1}>
              Open the{" "}
              <a
                className="font-medium text-slate-900 hover:underline"
                href="https://yivi.app/#download"
                target="_blank"
                rel="noopener noreferrer"
              >
                Yivi app
              </a>{" "}
              on your phone.
            </Step>
            <Step n={2}>Scan the QR code shown above.</Step>
            <Step n={3}>Approve disclosure of your email credential.</Step>
          </ol>
        </CardContent>

        <CardFooter className="flex flex-col gap-2 border-t border-slate-100 pt-6 text-center text-xs text-slate-500">
          <p>
            Need help? Visit our{" "}
            <a
              href="https://yivi.app/faq/"
              className="font-medium text-slate-700 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              FAQ
            </a>{" "}
            or email{" "}
            <a
              href="mailto:support@yivi.app"
              className="font-medium text-slate-700 hover:underline"
            >
              support@yivi.app
            </a>
            .
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

function Step({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <li className="flex gap-3">
      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-700">
        {n}
      </span>
      <span>{children}</span>
    </li>
  );
}
