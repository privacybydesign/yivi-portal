/* eslint-disable @typescript-eslint/no-explicit-any */
import { apiEndpoint } from "@/services/axiosInstance";
import useStore from "@/store";
import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function Login() {
  const setAccessToken = useStore((state) => state.setAccessToken);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    let web: any;
    import("@privacybydesign/yivi-frontend").then((yivi: any) => {
      web = yivi.newWeb({
        debugging: import.meta.env.DEV,
        element: "#yivi-web-form",
        language: "en",
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

      web.start().then((result: any) => {
        setAccessToken(result.access);
        if (location.state?.from) {
          navigate(location.state.from.pathname, { replace: true });
        } else {
          navigate(-1);
        }
      });
    });

    return () => web?.abort();
  }, [navigate, setAccessToken, location]);

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-10">
      <p className="mb-3 text-gray-600 text-start max-w-md">
        Scan the QR code with your Yivi app to authenticate with your email. If
        you don't have the app, you can download it{" "}
        <a
          className="text-blue-600 hover:underline"
          href="https://yivi.app/#download"
        >
          here
        </a>
        .
      </p>

      <div
        id="yivi-web-form"
        data-testid="yivi-web-form"
        className="mb-8 max-w-md w-full"
      ></div>
      <p className="my-10 text-gray-600 text-start">
        Having trouble? Read our{" "}
        <a
          href="https://yivi.app/faq/"
          className="text-blue-600 hover:underline"
        >
          frequently asked questions
        </a>{" "}
        or contact us at{" "}
        <a
          href="mailto:support@yivi.app"
          className="text-blue-600 hover:underline"
        >
          support@yivi.app
        </a>
        .
      </p>
    </div>
  );
}
