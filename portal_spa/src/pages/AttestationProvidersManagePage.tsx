import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";

export default function AttestationProvider() {
  return (
    <ManageOrganizationLayout>
      <div className="flex flex-col items-center justify-center h-80 bg-muted rounded-2xl shadow-inner">
        <h2 className="text-2xl font-semibold mb-2">Under Development</h2>
        <p className="text-muted-foreground text-center max-w-md">
          {"This section is coming soon. Stay tuned for updates!"}
        </p>
      </div>
    </ManageOrganizationLayout>
  );
}

AttestationProvider.getLayout = ManageOrganizationLayout;
