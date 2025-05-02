import { RequestCookie } from "next/dist/compiled/@edge-runtime/cookies";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { AuthToken } from "./models/auth_token";
import { jwtDecode } from "jwt-decode";

const isAuthenticated = (request: NextRequest): NextResponse | undefined => {
  // We can't access the access token, so we need to make due with the refresh token for now.
  // If there's a better strategy for validating if a user is authenticated, feel free to change it. :)
  if (!request.cookies.has("refresh_token")) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";

    return NextResponse.redirect(url);
  }
};

const canManageOrganization = (
  request: NextRequest,
): NextResponse | undefined => {
  const protectedRoute = "/manage";
  const url = request.nextUrl.clone();
  const token = request.cookies.get("refresh_token") as RequestCookie;
  const organizationSlug = jwtDecode<AuthToken>(token.value).organizationSlug;

  if (
    url.pathname.endsWith(protectedRoute) &&
    !url.pathname.includes(`/${organizationSlug}/`)
  ) {
    url.pathname = url.pathname.substring(
      0,
      url.pathname.length - protectedRoute.length,
    );

    return NextResponse.redirect(url);
  }
};

export function middleware(request: NextRequest) {
  return isAuthenticated(request) || canManageOrganization(request);
}

export const config = {
  matcher: "/organizations/(.*)",
};
