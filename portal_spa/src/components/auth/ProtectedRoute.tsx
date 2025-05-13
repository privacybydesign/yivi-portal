// ProtectedRoute.tsx
import React from "react";
import { Navigate, Outlet, useLocation, useParams } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedRoute: React.FC<{ organizationSlug?: string }> = ({
  organizationSlug,
}) => {
  const {
    accessToken,
    organizationSlug: userOrgSlug,
    initialized,
  } = useStore();
  const location = useLocation();
  const { organization } = useParams();

  if (!initialized) return null;
  if (!accessToken)
    return <Navigate to="/login" state={{ from: location }} replace />;

  if (organizationSlug && userOrgSlug !== organization) {
    return <Navigate to={`/organizations/${userOrgSlug}/manage`} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
