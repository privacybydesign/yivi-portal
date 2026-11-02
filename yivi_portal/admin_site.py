"""Django admin with Yivi as the second factor.

The password is the first factor. The second is a Yivi disclosure of the email
address on the staff account: the admin only opens once a valid disclosure of
``settings.EMAIL_DISCLOSURE`` yields the same address as ``user.email``.

The check sits in ``has_permission``, which guards every admin view, so a
session that only passed the password form cannot reach any admin page.
"""

import logging

import requests
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from yivi_auth.yivi import YiviException, YiviServer

logger = logging.getLogger(__name__)

# Holds the pk of the user whose email was disclosed, so a flag left behind by
# one account never counts for another.
VERIFIED_SESSION_KEY = "admin_yivi_verified_user"
TOKEN_SESSION_KEY = "admin_yivi_session_token"


def disclosed_email(result):
    """Return the email address from a successful disclosure, or None."""
    if not result:
        return None
    if result.get("status") != "DONE" or result.get("proofStatus") != "VALID":
        return None

    allowed = {
        attribute
        for discon in settings.EMAIL_DISCLOSURE
        for con in discon
        for attribute in con
    }
    for con in result.get("disclosed") or []:
        for attribute in con:
            if attribute.get("id") in allowed and attribute.get("status") == "PRESENT":
                return attribute.get("rawvalue")
    return None


def _same_email(disclosed, account):
    if not disclosed or not account:
        return False
    return disclosed.strip().casefold() == account.strip().casefold()


class YiviAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return self._password_verified(request) and self._yivi_verified(request)

    def _password_verified(self, request):
        """Active staff, logged in with a password: the first factor only."""
        return super().has_permission(request)

    @staticmethod
    def _yivi_verified(request):
        return request.session.get(VERIFIED_SESSION_KEY) == str(request.user.pk)

    def _next_url(self, request):
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return next_url
        return reverse("admin:index", current_app=self.name)

    @staticmethod
    def _query(request):
        return f"?{request.GET.urlencode()}" if request.GET else ""

    def get_urls(self):
        return [
            path("yivi/", self.yivi_verify, name="yivi_verify"),
            path("yivi/session/", self.yivi_start, name="yivi_start"),
            path("yivi/result/", self.yivi_result, name="yivi_result"),
            *super().get_urls(),
        ]

    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        # A staff user past the password form lands here again when
        # has_permission turns them away; send them on to the Yivi step.
        if (
            request.method == "GET"
            and self._password_verified(request)
            and not self._yivi_verified(request)
        ):
            return HttpResponseRedirect(
                reverse("admin:yivi_verify", current_app=self.name)
                + self._query(request)
            )
        return super().login(request, extra_context)

    @method_decorator(never_cache)
    def yivi_verify(self, request):
        if not self._password_verified(request):
            return HttpResponseRedirect(
                reverse("admin:login", current_app=self.name) + self._query(request)
            )
        if self._yivi_verified(request):
            return HttpResponseRedirect(self._next_url(request))

        context = {
            **self.each_context(request),
            "title": "Confirm with Yivi",
            "account_email": request.user.email,
            "yivi_config": {
                "startUrl": reverse("admin:yivi_start", current_app=self.name),
                "resultUrl": reverse("admin:yivi_result", current_app=self.name),
                "next": self._next_url(request),
                "csrfToken": get_token(request),
            },
        }
        request.current_app = self.name
        return TemplateResponse(request, "admin/yivi_verify.html", context)

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    @method_decorator(require_POST)
    def yivi_start(self, request):
        if not self._password_verified(request):
            return JsonResponse(
                {"detail": "Log in with your password first."}, status=403
            )

        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            response = yivi_server.start_session(
                {
                    "@context": "https://irma.app/ld/request/disclosure/v2",
                    "disclose": settings.EMAIL_DISCLOSURE,
                }
            )
        except (YiviException, requests.RequestException):
            logger.exception("Could not start the admin Yivi session")
            response = None
        if not response or "token" not in response:
            return JsonResponse(
                {"detail": "Could not start a Yivi session."}, status=502
            )

        # The requestor token stays on the server: the result is fetched with
        # the one stored here, never with one the browser sends back.
        request.session[TOKEN_SESSION_KEY] = response["token"]
        return JsonResponse({k: v for k, v in response.items() if k != "token"})

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    @method_decorator(require_POST)
    def yivi_result(self, request):
        if not self._password_verified(request):
            return JsonResponse(
                {"detail": "Log in with your password first."}, status=403
            )

        # One result per session: a failed attempt has to start a new one.
        token = request.session.pop(TOKEN_SESSION_KEY, None)
        if token is None:
            return JsonResponse({"detail": "No Yivi session in progress."}, status=400)

        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            result = yivi_server.session_result(token)
        except (YiviException, requests.RequestException):
            logger.exception("Could not fetch the admin Yivi session result")
            return JsonResponse(
                {"detail": "Could not reach the Yivi server."}, status=502
            )

        if not _same_email(disclosed_email(result), request.user.email):
            logger.warning(
                "Admin Yivi verification failed for user %s", request.user.pk
            )
            return JsonResponse(
                {"detail": "The disclosed email address does not match this account."},
                status=403,
            )

        request.session.cycle_key()
        request.session[VERIFIED_SESSION_KEY] = str(request.user.pk)
        return JsonResponse({"verified": True})
