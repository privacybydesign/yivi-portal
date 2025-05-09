import { useRoutes } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import OrganizationsListPage from "@/pages/OrganizationsListPage";
import OrgzanizationManagePage from "@/pages/OrganizationManagePage";
import MaintainerManagePage from "@/pages/MaintainerManagePage";
import OrganizationDetailsPage from "@/pages/OrganizationDetailsPage";
import RelyingPartiesManagePage from "@/pages/RelyingPartiesManagePage";
import LoginPage from "@/pages/LoginPage";
import OrganizationRegisterPage from "@/pages/OrganizationRegisterPage";
import Layout from "@/components/layout/Layout";

// We manage all routes here to keep App.tsx clean
export default function AppRoutes() {
  return useRoutes([
    {
      path: "/",
      element: <Layout />,
      children: [
        { path: "/", element: <HomePage /> },
        { path: "/organizations", element: <OrganizationsListPage /> },
        { path: "/login", element: <LoginPage /> },
        {
          path: "organizations/register",
          element: <OrganizationRegisterPage />,
        },
        {
          path: "/organizations/:organization",
          element: <OrganizationDetailsPage />,
        },
        {
          path: "/organizations/:organization/manage",
          element: <OrgzanizationManagePage />,
        },
        {
          path: "/organizations/:organization/manage/maintainers",
          element: <MaintainerManagePage />,
        },
        {
          path: "/organizations/:organization/manage/relying-parties",
          element: <RelyingPartiesManagePage />,
        },
      ],
    },
  ]);
}
