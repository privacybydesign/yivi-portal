import { useEffect } from "react";
import { Link, useNavigate, useLocation, matchRoutes } from "react-router-dom";
import { createAvatar } from "@dicebear/core";
import { initials } from "@dicebear/collection";
import useStore from "@/store";
import { axiosInstance } from "@/services/axiosInstance";
import { Avatar, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { useOrganizationNames } from "@/contexts/organization/OrganizationContext";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "../LanguageSwitcher";

export default function Header() {
  const initializeAuth = useStore((state) => state.initializeAuth);
  const navigate = useNavigate();
  const location = useLocation();
  const email = useStore((state) => state.email);
  const role = useStore((state) => state.role);
  const organizationSlugs = useStore((state) => state.organizationSlugs);
  const setAccessToken = useStore((state) => state.setAccessToken);
  const organizationNames = useOrganizationNames();
  const { t } = useTranslation();

  const svg = createAvatar(initials, {
    seed: email ?? "default-user",
    radius: 50,
    backgroundColor: ["d1d4f9", "ffd5dc", "c0aede"],
  }).toString();

  const handleLogout = async () => {
    const isOnProtectedRoute = matchRoutes(
      [
        { path: "organizations/:organization/manage" },
        { path: "organizations/:organization/manage/:section" },
        { path: "organizations/register" },
      ],
      location.pathname
    );

    if (isOnProtectedRoute?.length) {
      navigate("/");
    }

    // Invalidate token after routing to prevent redirecting to /login.
    await axiosInstance.post("/v1/logout");
    setAccessToken(null);
  };

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <div className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <nav className="container mx-auto flex justify-between items-center px-4 py-3">
        <Link to="/" className="text-xl font-semibold flex items-center gap-4">
          <img src="/yivi-logo.svg" alt="Yivi Logo" height={32} width={54} />
          Portal
        </Link>

        <div className="flex items-center gap-6">
          <Link
            to="/organizations"
            className={cn(
              buttonVariants({
                variant: "ghost",
                className:
                  location.pathname === "/organizations"
                    ? "bg-muted hover:bg-muted"
                    : "",
              })
            )}
          >
            {t("organizations")}
          </Link>

          {email ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded">
                  <Avatar className="h-9 w-9">
                    <AvatarImage
                      src={`data:image/svg+xml;utf8,${encodeURIComponent(svg)}`}
                      alt="User Avatar"
                    />
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{email}</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {role}
                    </p>
                  </div>
                </DropdownMenuLabel>

                {organizationSlugs.length > 0 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuLabel>{t("organizations")}</DropdownMenuLabel>
                    <DropdownMenuGroup>
                      {organizationSlugs.map((slug) => (
                        <Link key={slug} to={`/organizations/${slug}/manage`}>
                          <DropdownMenuItem className="!cursor-pointer">
                            {organizationNames[slug] || slug}
                          </DropdownMenuItem>
                        </Link>
                      ))}
                    </DropdownMenuGroup>
                  </>
                )}

                <DropdownMenuSeparator />

                <DropdownMenuItem
                  onClick={handleLogout}
                  className="!cursor-pointer"
                >
                  {t("logout")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link to="/login" className={cn(buttonVariants())}>
              {t("login")}
            </Link>
          )}
          <LanguageSwitcher />
        </div>
      </nav>
    </div>
  );
}
