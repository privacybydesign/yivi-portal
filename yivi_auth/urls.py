from django.urls import path

from yivi_auth import views

app_name = "yivi_auth"

urlpatterns = [
    path("v1/session/", views.YiviSessionProxyStartView.as_view(), name="start"),
    path(
        "v1/token/<str:yivi_token>",
        views.YiviSessionProxyResultView.as_view(),
        name="token_obtain_pair",
    ),
    path("v1/refreshtoken", views.RefreshTokenView.as_view(), name="token_refresh"),
    path("v1/logout", views.LogoutView.as_view(), name="logout"),
    path("v1/demo-issuance", views.YiviIssueDemosView.as_view(), name="demo_issuance"),
    path(
        "v1/demo-issuance/token/<str:yivi_token>",
        views.YiviDemoIssuanceResultView.as_view(),
        name="demo_issuance_token",
    ),
]
