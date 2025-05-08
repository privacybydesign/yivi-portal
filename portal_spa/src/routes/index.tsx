import { useRoutes } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import Layout from "@/components/layout/Layout";

// We manage all routes here to keep App.tsx clean
export default function AppRoutes() {
  return useRoutes([
    {
      path: "/",
      element: <Layout />,
      children: [{ path: "/", element: <HomePage /> }],
    },
  ]);
}
