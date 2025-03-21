/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import useStore from "@/src/store";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import getConfig from "next/config";

export default function Login() {
  const { publicRuntimeConfig } = getConfig();
  const accessToken = useStore((state) => state.accessToken);
  const setAccessToken = useStore((state) => state.setAccessToken)
  const router = useRouter();

  useEffect(() => {
    import("@privacybydesign/yivi-frontend").then((yivi: any) => {
      const web = yivi.newWeb({
        debugging: false,            // Enable to get helpful output in the browser console
        element:   '#yivi-web-form', // Which DOM element to render to
      
        // Back-end options
        session: {
          // Point this to your controller:
          url: publicRuntimeConfig.API_ENDPOINT + '/v1',
      
          start: {
            url: (o: any) => `${o.url}/session/`,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              '@context': 'https://irma.app/ld/request/disclosure/v2',
              'disclose': [
                [
                  ['pbdf.pbdf.email.email'],
                  ['pbdf.sidn-pbdf.email.email'],
                ]
              ]
            }),
            method: 'POST'
          },
          result: {
            url: (o: any, { sessionToken}: any) => `${o.url}/token/${sessionToken}`,
            method: 'GET'
          }
        }
      });
      web.start()
        .then((result: any) => {
          console.log(result.access);
          setAccessToken(result.access);
          router.push('/organizations');
        })
        .catch((err: any) => {
          alert(err);
        });
    });
  }, [router, setAccessToken]);

  return (
    <div className="flex justify-center items-center">
      <div className="flex grow p-6 justify-center items-center">
        <div id="yivi-web-form">
        </div>
        {accessToken}
      </div>
    </div>
  );
}