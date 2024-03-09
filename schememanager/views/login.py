import logging

from django.contrib.auth import get_user_model, login, logout
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    RedirectView,
)

from yivi_auth.signals import yivi_session_done

logger = logging.getLogger()


class LoginView(TemplateView):
    template_name = "login.html"

    yivi_request = {
        "@context": "https://irma.app/ld/request/disclosure/v2",
        "disclose": [[["pbdf.sidn-pbdf.email.email"]]],
    }

    success_url = reverse_lazy("schememanager:organization-list")

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url and next_url.startswith("/"):
            return next_url
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["yivi_request"] = self.yivi_request
        context["next_url"] = self.get_success_url()
        return context

    def dispatch(self, request, *args, **kwargs):
        """Redirect after login."""
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin:index")
        if request.session.get("yivi_email", None):
            return redirect("schememanager:index")
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def yivi_email_disclosure_login(request, email):
        """Log the user in based on the Yivi email disclosure."""
        request.session["yivi_email"] = email

        logger.info(f"User with email {email} logged in via Yivi.")

        user_model = get_user_model()
        try:
            user = user_model.objects.filter(email=email).get()
        except user_model.DoesNotExist:
            pass
        except user_model.MultipleObjectsReturned:
            raise RuntimeError(
                f"Multiple users found for email {email}. This should not happen."
            )
        else:
            login(request, user)

    @staticmethod
    @receiver(yivi_session_done)
    def yivi_session_done_handler(sender, request, result, yivi_session, **kwargs):
        if not (
            yivi_session["original_path"] == "/login/"
            and yivi_session["request"] == LoginView.yivi_request
        ):
            return

        yivi_email = result["disclosed"][0][0]["rawvalue"]
        LoginView.yivi_email_disclosure_login(request, yivi_email)


class LogoutView(RedirectView):
    pattern_name = "schememanager:index"

    def dispatch(self, request, *args, **kwargs):
        """Redirect after logout."""
        if request.session["yivi_email"]:
            del self.request.session["yivi_email"]

            logger.info(f"User with email {request.user.email} logged out.")

        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)
