import React, { useEffect, useState } from "react";
import { Navigate, Outlet, useParams } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedOrganizationRoute: React.FC = () => {
  const { organizationSlugs, initialized } = useStore();
  const { organization } = useParams();

  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    if (
      initialized &&
      organization &&
      !organizationSlugs?.includes(organization)
    ) {
      setShouldRedirect(true);
    }
  }, [initialized, organization, organizationSlugs]);

  if (!initialized) {
    return null;
  }

  if (shouldRedirect) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

export default ProtectedOrganizationRoute;
