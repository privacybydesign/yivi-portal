from django.urls import path

from schememanager import views

app_name = "schememanager"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegistrationView.as_view(), name="registration"),
    path("portal/", views.OrganizationListView.as_view(), name="organization-list"),
    path(
        "portal/<slug:slug>/",
        views.OrganizationPortalView.as_view(),
        name="organization-portal",
    ),
    path(
        "portal/<slug:slug>/admins/",
        views.OrganizationAdminsView.as_view(),
        name="organization-admins",
    ),
    path(
        "portal/<slug:slug>/verifier/",
        views.VerifierPortalView.as_view(),
        name="verifier-portal",
    ),
    path(
        "portal/<slug:slug>/verifier/hostnames/",
        views.VerifierHostnamesView.as_view(),
        name="verifier-hostnames",
    ),
    path(
        "portal/<slug:slug>/verifier/requests/",
        views.VerifierSessionRequestsView.as_view(),
        name="verifier-session-requests",
    ),
    path(
        "portal/<slug:slug>/issuer/",
        views.IssuerPortalView.as_view(),
        name="issuer-portal",
    ),
]
