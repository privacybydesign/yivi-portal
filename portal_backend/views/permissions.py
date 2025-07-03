import logging
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View
from ..models.models import User
from rest_framework_simplejwt.tokens import AccessToken  # type: ignore

logger = logging.getLogger(__name__)


class ORPermission(permissions.BasePermission):
    def __init__(self, *perms: permissions.BasePermission) -> None:
        self.perms: tuple[permissions.BasePermission, ...] = perms

    def has_permission(self, request: Request, view: View) -> bool:
        return any(perm().has_permission(request, view) for perm in self.perms)

    def has_object_permission(self, request: Request, view: View, obj: object) -> bool:
        return any(
            perm().has_object_permission(request, view, obj) for perm in self.perms
        )


class IsOrganizationMaintainerOrAdmin(permissions.BasePermission):
    message: str = (
        "Unauthorized: User does not have organization maintainer permissions"
    )

    def has_permission(self, request: Request, view: View) -> bool:
        request_org_slug: str | None = view.kwargs.get("org_slug")
        if request_org_slug is None:  # checking if org slug is present in the request
            return False

        if hasattr(request, "auth"):
            raw_token: AccessToken = str(request.auth)
            token = AccessToken(raw_token)
            token_org_slugs = token.get("organizationSlugs")

        try:
            user_obj = User.objects.get(email=request.user.email)
        except User.DoesNotExist:
            return False

        if user_obj.role == "admin":
            return True

        if user_obj.role == "maintainer":
            if request_org_slug in token_org_slugs:
                return True

        return False
