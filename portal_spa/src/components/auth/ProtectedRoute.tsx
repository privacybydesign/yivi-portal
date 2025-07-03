import React, { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import useStore from "@/store/index";
import { useTranslation } from "react-i18next";

const ProtectedRoute: React.FC = () => {
  const { accessToken, initialized } = useStore();
  const location = useLocation();
  const [showMessage, setShowMessage] = useState(true);
  const { t } = useTranslation();

  useEffect(() => {
    if (initialized && !accessToken) {
      setShowMessage(true);
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
            {t("auth.not_authenticated")}
          </div>
        </div>
      );
    }
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
