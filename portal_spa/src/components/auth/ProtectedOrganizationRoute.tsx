import React from "react";
import { Navigate, Outlet, useParams } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedOrganizationRoute: React.FC = () => {
  const { organizationSlugs, initialized } = useStore();
  const { organization } = useParams();

  if (!initialized || !organization) {
    return null;
  }

  if (initialized && !organizationSlugs?.includes(organization)) {
    return <Navigate to="/" />;
  }

  return <Outlet />;
};

export default ProtectedOrganizationRoute;
