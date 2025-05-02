import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // We can't access the access token, so we need to make due with the refresh token for now.
  // If there's a better strategy for validating if a user is authenticated, feel free to change it. :)
  if (!request.cookies.has("refresh_token")) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";

    return NextResponse.redirect(url);
  }
}

export const config = {
  matcher: "/organizations/(.*)",
};
