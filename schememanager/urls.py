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
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegistrationView.as_view(), name="registration"),
    path("portal/orgs/", OrganizationListView.as_view(), name="organization-list"),
    path(
        "portal/orgs/<slug:org_slug>/",
        OrganizationLegalPortalView.as_view(),
        name="organization-portal",
    ),
    path(
        "portal/orgs/<slug:org_slug>/billing/",
        OrganizationBillingPortalView.as_view(),
        name="organization-billing",
    ),
    path(
        "portal/orgs/<slug:org_slug>/admins/",
        OrganizationAdminsView.as_view(),
        name="organization-admins",
    ),
    path(
        "portal/verifiers/",
        VerifierListView.as_view(),
        name="verifier-list",
    ),
    path(
        "portal/verifiers/<slug:scheme>.<slug:verifier_slug>/",
        VerifierStatusView.as_view(),
        name="verifier-status",
    ),
    path(
        "portal/verifiers/<slug:scheme>.<slug:verifier_slug>/details/",
        VerifierDetailView.as_view(),
        name="verifier-portal",
    ),
    path(
        "portal/verifiers/<slug:scheme>.<slug:verifier_slug>/hostnames/",
        VerifierHostnamesView.as_view(),
        name="verifier-hostnames",
    ),
    path(
        "portal/verifiers/<slug:scheme>.<slug:verifier_slug>/requests/",
        VerifierSessionRequestsView.as_view(),
        name="verifier-session-requests",
    ),
    path(
        "portal/verifiers/<slug:scheme>.<slug:verifier_slug>/delete/",
        VerifierDeleteView.as_view(),
        name="verifier-delete",
    ),
    path(
        "portal/issuers/",
        IssuerPortalView.as_view(),
        name="issuer-list",
    ),
]
