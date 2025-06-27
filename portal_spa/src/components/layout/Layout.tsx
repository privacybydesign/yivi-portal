import { useEffect, useState } from "react";
import { Link, Outlet } from "react-router-dom";
import Header from "@/components/layout/Header";
import { OrganizationContext } from "@/contexts/organization/OrganizationContext";
import { axiosInstance } from "@/services/axiosInstance";
import useStore from "@/store";
import { buttonVariants } from "../ui/button";
import { cn } from "@/lib/utils";
import type { Organization } from "@/models/organization";

export default function Layout() {
  const [organizationNames, setOrganizationNames] = useState<
    Record<string, string>
  >({});
  const organizationSlugs = useStore((state) => state.organizationSlugs);

  useEffect(() => {
    const fetchOrganizationNames = async () => {
      try {
        const { data } = await axiosInstance.get(`/v1/profile`);

        const namesMap: Record<string, string> = {};
        organizationSlugs.forEach((slug) => {
          const org = data.find(
            (org: Partial<Organization>) => org.slug === slug
          );
          namesMap[slug] = org?.name_en || slug;
        });

        setOrganizationNames(namesMap);
      } catch (error) {
        console.error("Error fetching organization names:", error);
      }
    };

    if (organizationSlugs.length > 0) {
      fetchOrganizationNames();
    }
  }, [organizationSlugs]);

  return (
    <OrganizationContext.Provider value={organizationNames}>
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />

        <main className="flex-grow p-4">
          <div className="mx-auto w-full">
            <Outlet />
          </div>
        </main>

        <footer className="bg-white border-t p-4 shadow mt-4">
          <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-center text-sm text-gray-500">
              &copy; 2025 Yivi Portal. All rights reserved.
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                to="/faq"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                FAQ
              </Link>
              <Link
                to="/terms-of-service"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                Terms of Service
              </Link>
              <Link
                to="/privacy-policy"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                Privacy Policy
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </OrganizationContext.Provider>
  );
}
