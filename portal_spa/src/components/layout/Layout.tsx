import { Outlet } from "react-router-dom";
import Header from "@/components/layout/Header";

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow p-4">
        <Outlet />
      </main>
      <footer className="bg-gray-100 text-center p-4">
        &copy; 2025 Yivi Portal. All rights reserved.
      </footer>
    </div>
  );
}
