import { useEffect, useState } from "react";
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

export default function AttributeIndexLayout() {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    axiosInstance.get("/v1/yivi/credentials/").then((res) => {
      setCredentials(res.data.credentials);
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

  const filtered = credentials.filter((cred) => {
    const q = searchQuery.toLowerCase();

    return (
      cred.attributes.some((attr) => attr.name_en?.toLowerCase().includes(q)) ||
      cred.name_en?.toLowerCase().includes(q) ||
      cred.org_name?.toLowerCase().includes(q) ||
      cred.ap_slug?.toLowerCase().includes(q)
    );
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
      <div className="absolute z-50 bg-white border rounded shadow w-full mt-1 max-h-80 overflow-auto">
        <ul className="divide-y divide-gray-100">
          {results.map((cred) => {
            const { credential_id, ap_slug, environment, name_en, id } = cred;
            if (!credential_id || !ap_slug || !environment) return null;

            return (
              <li key={id} className="p-2 hover:bg-gray-100">
                <Link
                  to={`/attribute-index/credentials/${environment}/${ap_slug}/${credential_id}`}
                  onClick={onSelect}
                  className="block text-sm font-medium text-gray-900"
                >
                  {name_en}
                </Link>
                <p className="text-xs text-gray-500">
                  {credential_id} ({environment})
                </p>
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
    <div className="container mx-auto flex">
      {/* Sidebar */}
      <aside className="w-72 border-r p-4 sticky top-0 h-screen">
        <Link to="/attribute-index" className="block mb-4">
          <h1 className="text-xl font-bold mb-4">Attribute Index</h1>
        </Link>
        <Separator className="my-4" />
        <ScrollArea className="h-screen pr-2">
          <Accordion
            type="multiple"
            defaultValue={["production", "staging", "demo"]}
          >
            {Object.entries(grouped).map(([env, aps]) => (
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
                            <Link
                              to={`/attribute-index/attestation-provider/${referenceCredential.org_slug}/${referenceCredential.environment}/${referenceCredential.ap_slug}`}
                            >
                              {organizationName}
                            </Link>
                          </AccordionTrigger>
                          <AccordionContent>
                            <ul className="ml-2 space-y-1">
                              {creds.map((c) => (
                                <li key={c.id}>
                                  <Link
                                    to={`/attribute-index/credentials/${c.environment}/${c.ap_slug}/${c.credential_id}`}
                                    className="text-sm"
                                  >
                                    {c.name_en}
                                  </Link>
                                </li>
                              ))}
                            </ul>
                          </AccordionContent>
                        </AccordionItem>
                      );
                    })}
                  </Accordion>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </ScrollArea>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6">
        <div className="relative mb-4">
          <Input
            type="text"
            placeholder="Search credentials, attributes or issuer"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {!isMainPage && searchQuery.length > 0 && (
            <SearchDropdown
              results={filtered}
              onSelect={() => setSearchQuery("")}
            />
          )}
        </div>

        {/* If we are on the main page, show browsable credentials cards */}
        {isMainPage && (
          <div className="space-y-4">
            {filtered.map((cred) => {
              const { id, name_en, credential_id, ap_slug, environment } = cred;

              return (
                <div key={id} className="border rounded-md p-4">
                  <h2 className="font-semibold">
                    <Link
                      to={`/attribute-index/credentials/${environment}/${ap_slug}/${credential_id}`}
                    >
                      {name_en} ({credential_id})
                    </Link>
                  </h2>

                  <p className="text-sm text-muted-foreground">
                    Environment: {environment}
                  </p>

                  {Array.isArray(cred.attributes) && (
                    <ul className="list-disc mt-2">
                      {cred.attributes.map((attr) => (
                        <ul key={attr.id}>{attr.name_en}</ul>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>
        )}
        {!isMainPage && <Outlet context={{ credentials }} />}
      </main>
    </div>
  );
}
