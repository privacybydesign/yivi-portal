/* eslint-disable @typescript-eslint/no-explicit-any */
import { apiEndpoint } from "@/services/axiosInstance";
import useStore from "@/store";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const setAccessToken = useStore((state) => state.setAccessToken);
  const navigate = useNavigate();

  useEffect(() => {
    let web: any;

    import("@privacybydesign/yivi-frontend").then((yivi: any) => {
      web = yivi.newWeb({
        debugging: import.meta.env.DEV, // Enable to get helpful output in the browser console
        element: "#yivi-web-form", // Which DOM element to render to

        // Back-end options
        session: {
          // Point this to your controller:
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
        navigate(-1); // Go back to the previous page
      });
    });

    return () => web.abort();
  }, [navigate, setAccessToken]);

  return (
    <div className="flex p-6 justify-center items-center">
      <div id="yivi-web-form"></div>
    </div>
  );
}
