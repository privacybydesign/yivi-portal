import React, { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import useStore from "@/store/index";

const ProtectedRoute: React.FC = () => {
  const { accessToken, initialized } = useStore();
  const location = useLocation();
  // Starts true and only turns false once, right before redirecting away.
  const [showMessage, setShowMessage] = useState(true);

  useEffect(() => {
    if (initialized && !accessToken) {
      const timer = setTimeout(() => {
        setShowMessage(false);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [initialized, accessToken]);

  if (!initialized) {
    return null;
  }

  if (!accessToken) {
    if (showMessage) {
      return (
        <div className="flex items-center justify-center font-semibold text-lg">
          <div className="p-4 bg-white shadow-lg rounded-lg border">
            You are not authenticated. Redirecting...
          </div>
        </div>
      );
    }
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
