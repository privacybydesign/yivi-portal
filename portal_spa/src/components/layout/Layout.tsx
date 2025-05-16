import { Link, Outlet } from "react-router-dom";
import Header from "@/components/layout/Header";

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow p-4">
        <Outlet />
      </main>
      <footer className="bg-gray-100 p-4">
        <div className="flex justify-between container px-4 mx-auto">
          <p>&copy; 2025 Yivi Portal. All rights reserved.</p>
          <div className="grid gap-6">
            <Link to="/privacy-policy">Privacy policy</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
