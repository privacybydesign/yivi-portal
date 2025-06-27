import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import useStore from "@/store/index";

const GuestRoute: React.FC = () => {
  const { accessToken, initialized } = useStore();

  if (!initialized) {
    return null;
  }

  if (accessToken) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

export default GuestRoute;
