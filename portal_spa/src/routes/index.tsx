import { useRoutes } from "react-router-dom";
import HomePage from "@/pages/HomePage";

// We Manage all routes here to keep App.tsx clean
export default function AppRoutes() {
  return useRoutes([{ path: "/", element: <HomePage /> }]);
}
