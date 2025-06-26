import { useEffect, useRef, useState } from "react";
import { Outlet, Link, useMatch } from "react-router-dom";
import { axiosInstance } from "@/services/axiosInstance";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import type { Credential } from "@/models/credential";
import { useLocation } from "react-router-dom";
import { Separator } from "../ui/separator";
import { Button } from "../ui/button";
import { HamburgerIcon } from "lucide-react";
import { Skeleton } from "../ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { filterAndRankCredentials } from "@/utils/credentialSearch";
export default function AttributeIndexLayout() {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  const asideRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    axiosInstance.get("/v1/yivi/all-credentials/").then((res) => {
      setCredentials(res.data);
    });
  }, []);

  // Group creds by environment, each org can have multiple APs so we group by org_slug and ap_slug, this is used for the sidebar accordion
  const grouped: Record<string, Record<string, Credential[]>> = {};
  credentials.forEach((c) => {
    const env = c.environment;
    if (!grouped[env]) grouped[env] = {};
    const key = `${c.org_slug}-${c.ap_slug}`;
    if (!grouped[env][key]) grouped[env][key] = [];
    grouped[env][key].push(c);
  });
  const environmentWeights: Record<string, number> = {
    production: 1,
    staging: 0.8,
    demo: 0.5,
  };
  const filtered = filterAndRankCredentials({
    query: searchQuery,
    credentials,
    environmentWeights,
    // If you want to filter by env in this component, add:
    // filterByEnv: { production: true, staging: true, demo: true }
  });

  const isMainPage = useMatch("/attribute-index");
  const location = useLocation();

  useEffect(() => {
    // Clearing search searchQuery when navigating to a different page (mainly from main page to details page so the search bar is cleared)
    setSearchQuery("");
  }, [location]);

  function SearchDropdown({
    results,
    onSelect,
  }: {
    results: Credential[];
    onSelect: () => void;
  }) {
    if (results.length === 0) return null;

    return (
      <div className="absolute z-40 bg-white rounded shadow w-full mt-[61px] max-h-80 overflow-auto">
        <ul className="divide-y divide-gray-100">
          {results.map((cred) => {
            const { credential_id, ap_slug, environment, name_en, id } = cred;
            if (!credential_id || !ap_slug || !environment) return null;

            return (
              <li key={id}>
                <Link
                  to={`/attribute-index/credentials/${environment}/${ap_slug}/${credential_id}`}
                  onClick={onSelect}
                  className="flex items-center justify-between p-2 hover:bg-gray-100 rounded cursor-pointer no-underline"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {name_en}
                    </div>
                    <p className="text-xs text-gray-500">
                      {credential_id} ({environment})
                    </p>
                  </div>
                  {cred.deprecated_since && (
                    <div className="ml-2 shrink-0">
                      <Badge variant="destructive">Deprecated</Badge>
                    </div>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }

  function capitalizeFirstLetter(string: string): string {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  return (
    <div
      className="max-w-7xl mx-auto relative flex flex-row bg-white rounded-lg shadow-md min-h-screen [--topbar-height:61px]"
      onClick={(e) => {
        const clickedOutsideMenu =
          !asideRef.current?.contains(e.target as HTMLElement) &&
          !menuRef.current?.contains(e.target as HTMLElement);

        // Close menu when clicked outside the menu or when navigating to a different page.
        if (clickedOutsideMenu || (e.target as HTMLElement).tagName === "A") {
          setMenuOpen(false);
        }
      }}
    >
      {/* Sidebar */}
      <aside
        ref={asideRef}
        className={
          `border-r md:rounded-l-lg md:min-w-72 h-[calc(100vh-var(--topbar-height))] fixed md:sticky top-[var(--topbar-height)] transition z-10 bg-white ` +
          (menuOpen
            ? `max-md:-translate-x-4`
            : `max-md:opacity-0 max-md:-translate-x-full`)
        }
      >
        <div className="px-4 pt-4 gap-y-4 flex flex-col bg-white z-10 rounded-tl-lg">
          <Link to="/attribute-index">
            <h1 className="text-xl font-bold">Attribute Index</h1>
          </Link>
          <Separator className="-ml-4 w-[calc(100%+2rem)]" />
        </div>
        <ScrollArea className="h-[calc(100%-var(--topbar-height))] p-4">
          <Accordion
            type="multiple"
            defaultValue={["production", "staging", "demo"]}
          >
            {Object.keys(grouped).length > 0 ? (
              Object.entries(grouped).map(([env, aps]) => (
                <AccordionItem value={env} key={env}>
                  <AccordionTrigger>
                    <Link to={`/attribute-index/environments/${env}`}>
                      {capitalizeFirstLetter(env)} Environment
                    </Link>
                  </AccordionTrigger>
                  <AccordionContent>
                    <Accordion type="multiple">
                      {Object.entries(aps).map(([key, creds]) => {
                        const referenceCredential = creds[0]; // Use the first credential as reference for org_slug and org_name
                        if (!referenceCredential) return null;
                        const organizationName = referenceCredential.org_name;
                        return (
                          <AccordionItem value={key} key={key}>
                            <AccordionTrigger>
                              <div className="mx-2 font-normal">
                                <Link
                                  to={`/attribute-index/attestation-provider/${referenceCredential.org_slug}/${referenceCredential.environment}/${referenceCredential.ap_slug}`}
                                >
                                  {organizationName}
                                </Link>
                              </div>
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="mx-3 font-light">
                                <ul className="ml-2 space-y-1.5">
                                  {creds.map((c) => (
                                    <li key={c.id}>
                                      <Link
                                        to={`/attribute-index/credentials/${c.environment}/${c.ap_slug}/${c.credential_id}`}
                                        className="text-sm hover:underline transition"
                                      >
                                        {c.name_en}
                                      </Link>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        );
                      })}
                    </Accordion>
                  </AccordionContent>
                </AccordionItem>
              ))
            ) : (
              <div className="space-y-4 mt-4">
                <Skeleton className="h-9"></Skeleton>
                <Skeleton className="ml-4 h-9"></Skeleton>
                <Skeleton className="ml-4 h-9"></Skeleton>
                <Skeleton className="h-9"></Skeleton>
                <Skeleton className="ml-4 h-9"></Skeleton>
                <Skeleton className="ml-4 h-9"></Skeleton>
              </div>
            )}
          </Accordion>
        </ScrollArea>
      </aside>

      {/* Main Content */}
      <main
        className={
          `p-6 overflow-x-auto w-full ` +
          (menuOpen
            ? `before:bg-[rgba(0,0,0,0.3)] before:h-full max-md:before:absolute before:inset-0 before:rounded-lg`
            : ``)
        }
      >
        <div className="relative flex flex-col gap-2 mb-4 -mt-6 -mx-6">
          <div className="md:hidden flex border-r border-b min-w-[var(--topbar-height)]">
            <Button
              variant="ghost"
              size="icon"
              className="m-auto"
              onClick={() => setMenuOpen(!menuOpen)}
              ref={menuRef}
            >
              <HamburgerIcon />
            </Button>
          </div>
          <Input
            type="text"
            placeholder="Search credentials, attributes or issuer"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-0 shadow-none h-[var(--topbar-height)] px-6 border-b rounded-none focus-visible:ring-[0px]"
          />
          {searchQuery.length > 0 && (
            <SearchDropdown
              results={filtered}
              onSelect={() => setSearchQuery("")}
            />
          )}
        </div>

        {/* If we are on the main page, show a description of what the attribute index is for */}
        {isMainPage ? (
          <div className="space-y-4 mx-2 my-10">
            <div className="text-lg font-semibold mb-4">
              What is the attribute index?
            </div>
            <div>
              <p className="leading-relaxed">
                The attribute index is a browsable list of all attributes that
                can be used in the Yivi ecosystem. It allows you to explore the
                available credentials and their definitions, and the
                organizations that issue them. You can search for specific
                attributes, credentials, or issuers using the search bar above.
                The sidebar provides a structured view of the credentials
                grouped by environment and attestation provider.
              </p>
            </div>
          </div>
        ) : (
          <div className="lg:p-4">
            <Outlet context={{ credentials }} />
          </div>
        )}
      </main>
    </div>
  );
}
