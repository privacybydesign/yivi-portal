import { useEffect, useState } from "react";
import { Link, Outlet } from "react-router-dom";
import Header from "@/components/layout/Header";
import { OrganizationContext } from "@/contexts/organization/OrganizationContext";
import { axiosInstance } from "@/services/axiosInstance";
import { useTranslation } from "react-i18next";
import useStore from "@/store";
import { buttonVariants } from "../ui/button";
import { cn } from "@/lib/utils";

export default function Layout() {
  const [organizationNames, setOrganizationNames] = useState<
    Record<string, string>
  >({});
  const organizationSlugs = useStore((state) => state.organizationSlugs);
  const { t } = useTranslation();

  useEffect(() => {
    const fetchOrganizationNames = async () => {
      const namesMap: Record<string, string> = {};
      await Promise.all(
        organizationSlugs.map(async (slug) => {
          try {
            const { data, status } = await axiosInstance.get(
              `/v1/organizations/${slug}`
            );
            namesMap[slug] =
              status === 200 && data.name_en ? data.name_en : slug;
          } catch (error) {
            console.error(
              `Error fetching organization name for ${slug}:`,
              error
            );
            namesMap[slug] = slug;
          }
        })
      );
      setOrganizationNames(namesMap);
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
                to="/terms-of-service"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                {t("terms")}
              </Link>
              <Link
                to="/privacy-policy"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                {t("privacy")}
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </OrganizationContext.Provider>
  );
}
