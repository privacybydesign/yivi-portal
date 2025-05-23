import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedRoute: React.FC = () => {
  const { accessToken, initialized } = useStore();
  const location = useLocation();
  if (!initialized) {
    return null;
  }

  if (!accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
