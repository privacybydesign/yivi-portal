import { useEffect, useState } from "react";
import { Link, Outlet } from "react-router-dom";
import Header from "@/components/layout/Header";
import { OrganizationContext } from "@/contexts/OrganizationContext";
import { axiosInstance } from "@/services/axiosInstance";
import useStore from "@/store";
import { buttonVariants } from "../ui/button";
import { cn } from "@/lib/utils";

export default function Layout() {
  const [organizationNames, setOrganizationNames] = useState<
    Record<string, string>
  >({});
  const organizationSlugs = useStore((state) => state.organizationSlugs);

  const fetchOrganizationName = async (slug: string) => {
    try {
      const response = await axiosInstance.get(`/v1/organizations/${slug}`);
      if (response.status === 200) {
        return response.data.name_en;
      }
      return slug;
    } catch (error) {
      console.error(`Error fetching organization name for ${slug}:`, error);
      return slug;
    }
  };

  useEffect(() => {
    const loadOrganizationNames = async () => {
      const slugMap: Record<string, string> = {};
      for (const slug of organizationSlugs) {
        const name = await fetchOrganizationName(slug);
        slugMap[slug] = name;
      }
      setOrganizationNames(slugMap);
    };

    if (organizationSlugs.length > 0) {
      loadOrganizationNames();
    }
  }, [organizationSlugs]);

  return (
    <OrganizationContext.Provider value={organizationNames}>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow p-4">
          <Outlet />
        </main>
        <footer className="bg-gray-100 p-4">
          <div className="flex justify-between items-center container px-4 mx-auto">
            <p>&copy; 2025 Yivi Portal. All rights reserved.</p>
            <div className="flex gap-6">
              <Link
                to="/terms-of-service"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                Terms of service
              </Link>
              <Link
                to="/privacy-policy"
                className={cn(buttonVariants({ variant: "link" }))}
              >
                Privacy policy
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </OrganizationContext.Provider>
  );
}
