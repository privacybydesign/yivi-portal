import React from "react";
import { Navigate, Outlet, useParams } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedOrganizationRoute: React.FC = () => {
  const { organizationSlugs, initialized } = useStore();
  const { organization } = useParams();

  if (!initialized) {
    return null;
  }

  if (!organizationSlugs?.includes(organization as string)) {
    return <Navigate to={`/`} replace />;
  }

  return <Outlet />;
};

export default ProtectedOrganizationRoute;
