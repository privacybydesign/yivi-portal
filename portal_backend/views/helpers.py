import logging
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View
from django.shortcuts import get_object_or_404
from ..models.models import User

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


class IsMaintainerOrAdmin(permissions.BasePermission):
    message: str = "Unauthorized: User does not have maintainer permissions"

    def has_permission(self, request: Request, view: View) -> bool:
        user_obj: User = get_object_or_404(User, email=request.user.email)
        return user_obj.role == "maintainer" or user_obj.role == "admin"


class BelongsToOrganization(permissions.BasePermission):
    message: str = "Unauthorized: User does not belong to this organization"

    def has_permission(self, request: Request, view: View) -> bool:
        logger.info(view.kwargs)
        org_pk: str | None = view.kwargs.get("pk")
        if org_pk is None:
            return False

        logger.info("Checking if user belongs to organization with id: " + str(org_pk))

        user_obj: User = get_object_or_404(User, email=request.user.email)
        if user_obj.role == "admin":
            return True
        if user_obj.organization.id == int(org_pk):
            return True

        return False
