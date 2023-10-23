from django.urls import path

from yivi_auth import views

app_name = "yivi_auth"

urlpatterns = [
    path("session/", views.YiviSessionProxyStartView.as_view(), name="start"),
    path(
        "session/<str:token>/result/",
        views.YiviSessionProxyResultView.as_view(),
        name="result",
    ),
]
