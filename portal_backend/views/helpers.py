from rest_framework import permissions
from django.shortcuts import get_object_or_404
from ..models.models import RelyingParty, User, Organization


class IsMaintainer(permissions.BasePermission):
    message = "Unauthorized: User does not have maintainer permissions"

    def has_permission(self, request, view):
        user_obj = get_object_or_404(User, email=request.user.email)
        return user_obj.role == "maintainer"


class BelongsToOrganization(permissions.BasePermission):
    message = "Unauthorized: User does not belong to this organization"

    def has_permission(self, request, view):
        org_pk = view.kwargs.get('org_pk')
        slug = view.kwargs.get('slug')

        user_obj = get_object_or_404(User, email=request.user.email)

        if org_pk:
            return str(user_obj.organization.id) == str(org_pk)
        elif slug:
            try:
                organization = Organization.objects.get(slug=slug)
                return user_obj.organization.id == organization.id
            except RelyingParty.DoesNotExist:
                return False

        return True  # if no org id found, skip this check
