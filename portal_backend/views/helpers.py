import logging
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from ..models.models import User

logger = logging.getLogger(__name__)

class ORPermission(permissions.BasePermission):
    def __init__(self, *perms):
        self.perms = perms

    def has_permission(self, request, view):
        return any(perm().has_permission(request, view) for perm in self.perms)

    def has_object_permission(self, request, view, obj):
        return any(perm().has_object_permission(request, view, obj) for perm in self.perms)


class IsMaintainerOrAdmin(permissions.BasePermission):
    message = "Unauthorized: User does not have maintainer permissions"

    def has_permission(self, request, view):
        user_obj = get_object_or_404(User, email=request.user.email)
        return user_obj.role == "maintainer" or user_obj.role == "admin"


class BelongsToOrganization(permissions.BasePermission):
    message = "Unauthorized: User does not belong to this organization"

    def has_permission(self, request, view):
        logger.info(view.kwargs)
        org_pk = view.kwargs.get("pk")
        if org_pk is None:
            return False
        
        logger.info("Checking if user belongs to organization with id: " + str(org_pk))

        user_obj = get_object_or_404(User, email=request.user.email)
        if user_obj.role == "admin":
            return True
        if user_obj.organization.id == org_pk:
            return True

        return False
