from django.urls import path

from schememanager.views.index import IndexView
from schememanager.views.issuer import *
from schememanager.views.login import *
from schememanager.views.organization import *
from schememanager.views.verifier import *

app_name = "schememanager"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegistrationView.as_view(), name="registration"),
    path("portal/", OrganizationListView.as_view(), name="organization-list"),
    path(
        "portal/<slug:org_slug>/",
        OrganizationLegalPortalView.as_view(),
        name="organization-portal",
    ),
    path(
        "portal/<slug:org_slug>/billing/",
        OrganizationBillingPortalView.as_view(),
        name="organization-billing",
    ),
    path(
        "portal/<slug:org_slug>/admins/",
        OrganizationAdminsView.as_view(),
        name="organization-admins",
    ),
    path(
        "portal/<slug:org_slug>/verifier/",
        VerifierListView.as_view(),
        name="verifier-list",
    ),
    path(
        "portal/<slug:org_slug>/verifier/<slug:scheme>.<slug:verifier_slug>/",
        VerifierStatusView.as_view(),
        name="verifier-status",
    ),
    path(
        "portal/<slug:org_slug>/verifier/<slug:scheme>.<slug:verifier_slug>/details/",
        VerifierDetailView.as_view(),
        name="verifier-portal",
    ),
    path(
        "portal/<slug:org_slug>/verifier/<slug:scheme>.<slug:verifier_slug>/hostnames/",
        VerifierHostnamesView.as_view(),
        name="verifier-hostnames",
    ),
    path(
        "portal/<slug:org_slug>/verifier/<slug:scheme>.<slug:verifier_slug>/requests/",
        VerifierSessionRequestsView.as_view(),
        name="verifier-session-requests",
    ),
    path(
        "portal/<slug:org_slug>/verifier/<slug:scheme>.<slug:verifier_slug>/delete/",
        VerifierDeleteView.as_view(),
        name="verifier-delete",
    ),
    path(
        "portal/<slug:org_slug>/issuer/",
        IssuerPortalView.as_view(),
        name="issuer-list",
    ),
]
