import OrganizationForm from "@/components/forms/organization/OrganizationForm";
import { Link } from "react-router-dom";

export default function RegisterOrganization() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex flex-col gap-6 mb-6 bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-1">Register Organization</h1>
        <OrganizationForm editMode={false}></OrganizationForm>
      </div>
      <div className="text-sm text-muted-foreground">
        By registering your organization, you can participate in the Yivi
        ecosystem as a relying party or an attestation provider. Your contact
        information will only be used for verification purposes.
        <br />
        <br />
        If you are already part of Yivi's echosystem as listed{" "}
        <Link to={`/organizations/`} className="text-blue-600">
          here
        </Link>
        , you will not need to fill this form again. Please contact us to be
        granted access and maintainer rights. You will receive an email once
        this has been processed.
        <br />
        <br />
        If you have any questions or need assistance, please contact us at{" "}
        <a
          href="mailto:support@yivi.app"
          className="text-blue-600 hover:underline"
        >
          support@yivi.app
        </a>
        .
      </div>
    </div>
  );
}
