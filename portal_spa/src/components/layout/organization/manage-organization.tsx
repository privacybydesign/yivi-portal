import type { ReactNode } from "react";
import { useParams } from "react-router-dom";
import { useOrganizationNames } from "@/contexts/organization/OrganizationContext";
import { SidebarNavigation } from "@/components/ui/sidebar-navigation";
import { Separator } from "@/components/ui/separator";
import { PageContainer } from "@/components/layout/PageContainer";

const menuItems = [
  { href: "/organizations/:organization/manage", title: "Basic information" },
  {
    href: "/organizations/:organization/manage/maintainers",
    title: "Maintainers",
  },
  {
    href: "/organizations/:organization/manage/relying-parties",
    title: "Relying parties",
  },
  {
    href: "/organizations/:organization/manage/attestation-providers",
    title: "Attestation providers",
  },
];

interface ManageOrganizationLayoutProps {
  children: ReactNode;
}

export default function ManageOrganizationLayout({
  children,
}: ManageOrganizationLayoutProps) {
  const { organization } = useParams<{ organization: string }>();
  const organizationNames = useOrganizationNames();
  // Match the organization slug to its name and find the corresponding name
  const organizationName = organization && organizationNames[organization];

  if (!organizationName) {
    return null;
  }

  return (
    <PageContainer>
      <div className="space-y-6 p-6 bg-white rounded-lg shadow-md min-h-screen">
        <div className="space-y-0.5">
          <h1 className="text-2xl font-bold tracking-tight">
            Manage {organizationName}
          </h1>
          <p className="text-muted-foreground">
            Manage your organization settings.
          </p>
        </div>

        <Separator className="my-6" />

        <div className="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
          <aside className="lg:w-1/5 overflow-x-auto scroll-shadows [--muted:rgba(219,219,219,0.25)]">
            <SidebarNavigation items={menuItems} />
          </aside>
          <div className="flex-1 lg:max-w-2xl">{children}</div>
        </div>
      </div>
    </PageContainer>
  );
}
