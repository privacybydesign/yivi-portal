import { useRoutes } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import OrganizationsListPage from "@/pages/OrganizationsListPage";
import OrgzanizationManagePage from "@/pages/OrganizationManagePage";
import MaintainerManagePage from "@/pages/MaintainerManagePage";
import OrganizationDetailsPage from "@/pages/OrganizationDetailsPage";
import RelyingPartiesManagePage from "@/pages/RelyingPartiesManagePage";
import AttestationProvidersManagePage from "@/pages/AttestationProvidersManagePage";
import LoginPage from "@/pages/LoginPage";
import OrganizationRegisterPage from "@/pages/OrganizationRegisterPage";
import Layout from "@/components/layout/Layout";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import PrivacyPolicyPage from "@/pages/PrivacyPolicyPage";
import ProtectedOrganizationRoute from "@/components/auth/ProtectedOrganizationRoute";
import GuestRoute from "@/components/auth/GuestRoute";
import EnvironmentDetailsPage from "@/pages/EnvironmentDetailsPage";
import AttestationProviderDetailsPage from "@/pages/AttestationProviderDetailsPage";
import CredentialDetailsPage from "@/pages/CredentialDetailsPage";
import AttributeIndexLayout from "@/components/layout/AttributeIndexLayout";
import FAQPage from "@/pages/FAQPage";

export default function AppRoutes() {
  return useRoutes([
    {
      path: "/",
      element: <Layout />,
      children: [
        { path: "/", element: <HomePage /> },
        {
          element: <GuestRoute />,
          children: [{ path: "/login", element: <LoginPage /> }],
        },
        { path: "/organizations", element: <OrganizationsListPage /> },
        {
          path: "/organizations/:organization",
          element: <OrganizationDetailsPage />,
        },
        {
          path: "/faq",
          element: <FAQPage />,
        },
        {
          element: <ProtectedRoute />,
          children: [
            {
              path: "/organizations/register",
              element: <OrganizationRegisterPage />,
            },
            {
              element: <ProtectedOrganizationRoute />,
              children: [
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
                {
                  path: "/organizations/:organization/manage/attestation-providers",
                  element: <AttestationProvidersManagePage />,
                },
              ],
            },
          ],
        },
        { path: "/privacy-policy", element: <PrivacyPolicyPage /> },
        {
          path: "/attribute-index",
          element: <AttributeIndexLayout />,
          children: [
            {
              path: "environments/:environment",
              element: <EnvironmentDetailsPage />,
            },
            {
              path: "attestation-provider/:org_slug/:environment/:ap_slug",
              element: <AttestationProviderDetailsPage />,
            },
            {
              path: "credentials/:environment/:ap_slug/:credential_id",
              element: <CredentialDetailsPage />,
            },
          ],
        },
      ],
    },
  ]);
}
