import type { ReactNode } from "react";
import { SidebarNavigation } from "@/components/ui/sidebar-navigation";
import { Separator } from "@/components/ui/separator";

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
  return (
    <div className="space-y-6 px-3 py-16 container mx-auto">
      <div className="space-y-0.5">
        <h1 className="text-2xl font-bold tracking-tight">
          Manage organization
        </h1>
        <p className="text-muted-foreground">
          Manage your organization settings.
        </p>
      </div>

      <Separator className="my-6" />

      <div className="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
        <aside className="-mx-4 lg:w-1/5">
          <SidebarNavigation items={menuItems} />
        </aside>
        <div className="flex-1 lg:max-w-2xl">{children}</div>
      </div>
    </div>
  );
}
