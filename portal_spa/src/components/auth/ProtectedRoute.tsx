import React from "react";
import { Navigate, Outlet, useLocation, useParams } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedRoute: React.FC = () => {
  const { accessToken, organizationSlugs, initialized } = useStore();
  const location = useLocation();
  const { organization } = useParams();

  if (!initialized) return null;
  if (!accessToken)
    return <Navigate to="/login" state={{ from: location }} replace />;

  if (!organizationSlugs?.includes(organization as string)) {
    return <Navigate to={`/`} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
