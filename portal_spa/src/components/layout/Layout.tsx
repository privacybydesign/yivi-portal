import { Link, Outlet } from "react-router-dom";
import Header from "@/components/layout/Header";
import { buttonVariants } from "../ui/button";
import { cn } from "@/lib/utils";

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow p-4">
        <Outlet />
      </main>
      <footer className="bg-gray-100 p-4">

        <div className="flex justify-between items-center container px-4 mx-auto">
          <p>&copy; 2025 Yivi Portal. All rights reserved.</p>
          <div className="flex gap-6">
            <Link
              to="/terms-of-service"
              className={cn(buttonVariants({ variant: "link" }))}
            >
              Terms of service
            </Link>
            <Link
              to="/privacy-policy"
              className={cn(buttonVariants({ variant: "link" }))}
            >
              Privacy policy
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
