import logging

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError, BadRequest
from django.db import IntegrityError
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views.generic import (
    DetailView,
    UpdateView,
    ListView,
    DeleteView,
)

from schememanager.forms.verifier import *
from schememanager.models.organization import Organization
from schememanager.models.scheme import Scheme
from schememanager.models.verifier import Verifier

logger = logging.getLogger()


class VerifierListView(ListView):
    template_name = "verifier/verifier_list.html"
    model = Verifier
    context_object_name = "verifiers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["schemes"] = Scheme.objects.filter(scheme_type=Scheme.REQUESTOR)
        return context

    def dispatch(self, request, *args, **kwargs):
        # If the user is not logged in, redirect to the login page
        if "yivi_email" not in request.session:
            url = reverse("schememanager:login")
            if request.method == "GET":
                url += "?" + urlencode({"next": request.path})
            return redirect(url)

        # If user does not have permission to view this page, raise PermissionDenied
        if (
            not self.get_organization()
            .admins.filter(email=request.session["yivi_email"])
            .exists()
        ):
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_organization(self):
        return get_object_or_404(Organization, slug=self.kwargs["org_slug"])

    def get_queryset(self):
        return self.get_organization().verifier_registrations.all()

    def register(self, scheme, slug):
        organization = self.get_organization()
        try:
            verifier = Verifier(
                scheme=scheme,
                slug=slug,
                organization=organization,
            )
            verifier.full_clean()
            verifier.save()
            logger.info(
                f"Verifier {verifier.full_id} was registered by {self.request.session['yivi_email']}."
            )
        except (ValidationError, IntegrityError):
            # Something went wrong creating the verifier
            messages.error(
                self.request,
                "Verifier with slug %s is not a valid slug or is already registered in this scheme."
                % slug,
            )
            return redirect(self.request.path)

        return redirect(
            "schememanager:verifier-portal",
            org_slug=verifier.organization.slug,
            scheme=verifier.scheme.id,
            verifier_slug=verifier.slug,
        )

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "register":
            # A POST request with a slug is used to register a new verifier
            scheme = get_object_or_404(Scheme, id=request.POST.get("scheme"))
            slug = request.POST.get("slug")
            return self.register(scheme, slug)
        else:
            raise BadRequest("Invalid action")


class VerifierPortalView(DetailView):
    model = Verifier
    context_object_name = "verifier"

    def dispatch(self, request, *args, **kwargs):
        # If the user is not logged in, redirect to the login page
        if "yivi_email" not in request.session:
            url = reverse("schememanager:login")
            if request.method == "GET":
                url += "?" + urlencode({"next": request.path})
            return redirect(url)

        # If user does not have permission to view this page, raise PermissionDenied
        if (
            not self.get_object()
            .organization.admins.filter(email=request.session["yivi_email"])
            .exists()
        ):
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            Verifier,
            scheme=self.kwargs["scheme"],
            slug=self.kwargs["verifier_slug"],
            organization__slug=self.kwargs["org_slug"],
        )


class VerifierDetailView(UpdateView, VerifierPortalView):
    template_name = "verifier/verifier_detail.html"
    form_class = VerifierForm

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.organization = get_object_or_404(
            Organization, slug=self.kwargs["org_slug"]
        )
        form.save()
        messages.success(self.request, "Your verifier has been updated.")
        logger.info(
            f"Verifier {form.instance.full_id} was updated by {self.request.session['yivi_email']}."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class VerifierHostnamesView(VerifierPortalView):
    template_name = "verifier/verifier_hostnames.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hostnames"] = self.get_object().hostnames.all()
        context["add_hostname_form"] = VerifierHostnameForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object():
            messages.error(self.request, "You must first register as a verifier.")
            return redirect("schememanager:verifier-list", org_slug=kwargs["org_slug"])
        return super().dispatch(request, *args, **kwargs)

    def add_hostname(self, hostname):
        # If the hostname is already registered, show an error
        if self.get_object().hostnames.filter(hostname=hostname).exists():
            messages.error(
                self.request, "%s is already registered as hostname." % hostname
            )
            return redirect(self.get_success_url())

        try:
            form = VerifierHostnameForm({"hostname": hostname})
            if not form.is_valid():
                messages.error(
                    self.request,
                    "Hostname %s is not a valid hostname." % hostname,
                )
                return redirect(self.get_success_url())
            form.instance.verifier = self.get_object()
            instance = form.save()
            logger.info(
                f"Hostname {instance.hostname} was added to verifier {instance.verifier} by {self.request.session['yivi_email']}."
            )
            if instance.dns_challenge_verified:
                messages.success(
                    self.request,
                    "%s was added as hostname and verified." % instance.hostname,
                )
                logger.info(f"Hostname {instance.hostname} was already verified.")
            else:
                messages.info(
                    self.request,
                    "%s was added as hostname, awaiting DNS verification."
                    % instance.hostname,
                )
        except IntegrityError:
            messages.error(
                self.request,
                "Hostname %s is already registered by another verifier." % hostname,
            )
        return redirect(self.get_success_url())

    def remove_hostname(self, hostname):
        self.get_object().hostnames.get(hostname=hostname).delete()
        messages.success(self.request, "%s was removed as hostname." % hostname)
        logger.info(
            f"Hostname {hostname} was removed from verifier {self.get_object().full_id} by {self.request.session['yivi_email']}."
        )
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if not self.get_object().can_be_edited:
            messages.error(self.request, "You cannot edit this verifier.")
            return redirect(self.get_success_url())

        if request.POST.get("action") == "remove":
            return self.remove_hostname(request.POST.get("hostname"))
        elif request.POST.get("action") == "add":
            return self.add_hostname(request.POST.get("hostname"))
        else:
            raise BadRequest("Invalid action")

    def get_success_url(self):
        return self.request.path


class VerifierSessionRequestsView(VerifierPortalView):
    template_name = "verifier/verifier_session_requests.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["session_requests"] = self.get_object().session_requests.all()
        context["add_session_request_form"] = VerifierSessionRequestAddForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object():
            messages.error(self.request, "You must first register as a verifier.")
            return redirect("schememanager:verifier-list", org_slug=kwargs["org_slug"])
        return super().dispatch(request, *args, **kwargs)

    def add_session_request(self, condiscon):
        form = VerifierSessionRequestAddForm({"condiscon": condiscon})
        if not form.is_valid():
            messages.error(self.request, "Condiscon is not valid.")
            return redirect(self.get_success_url())
        form.instance.verifier = self.get_object()

        if form.instance.verifier.session_requests.filter(
            condiscon=form.instance.condiscon
        ).exists():
            messages.error(
                self.request,
                "Session request with this condiscon is already registered.",
            )
            return redirect(self.get_success_url())

        form.save()
        messages.info(self.request, "Session request was added.")
        logger.info(
            f"Session request {form.instance.condiscon} was added to verifier {form.instance.verifier.full_id} by {self.request.session['yivi_email']}."
        )
        return redirect(self.get_success_url())

    def update_session_request(self, session_request, request):
        session_request.context_description_en = request.POST.get("context-en")
        session_request.context_description_nl = request.POST.get("context-nl")
        session_request.save()

        attribute_reasons = {
            attribute_id: {
                "en": request.POST["reason-en-" + attribute_id],
                "nl": request.POST["reason-nl-" + attribute_id],
            }
            for attribute_id in session_request.condiscon_attributes
        }
        for attribute in session_request.attributes.all():
            attribute.reason_en = attribute_reasons[attribute.attribute_id]["en"]
            attribute.reason_nl = attribute_reasons[attribute.attribute_id]["nl"]
            attribute.save()

        messages.success(self.request, "Session request was updated.")
        logger.info(
            f"Session request {session_request.condiscon} was updated by {self.request.session['yivi_email']}."
        )

        return redirect(self.get_success_url())

    def remove_session_request(self, session_request_id):
        self.get_object().session_requests.get(id=session_request_id).delete()
        messages.success(self.request, "Session request was removed.")
        logger.info(
            f"Session request {session_request_id} was removed from verifier {self.get_object().full_id} by {self.request.session['yivi_email']}."
        )
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if not self.get_object().can_be_edited:
            messages.error(self.request, "You cannot edit this verifier.")
            return redirect(self.get_success_url())

        if request.POST.get("action") == "remove":
            return self.remove_session_request(request.POST.get("session_request"))
        elif request.POST.get("action") == "update":
            session_request_id = request.POST.get("session_request")
            session_request = self.get_object().session_requests.get(
                id=session_request_id
            )
            return self.update_session_request(session_request, request)
        elif request.POST.get("action") == "add":
            try:
                return self.add_session_request(request.POST.get("condiscon"))
            except ValidationError:
                messages.error(self.request, "Invalid session request condiscon.")
                return redirect(self.get_success_url())
        else:
            raise BadRequest("Invalid action")

    def get_success_url(self):
        return self.request.path


class VerifierStatusView(VerifierPortalView):
    template_name = "verifier/verifier_status.html"

    def register_ready_for_review(self):
        obj = self.get_object()
        obj.ready = True
        obj.ready_at = timezone.now()

        if not obj.scheme.production:
            obj.reviewed_accepted = True
            obj.reviewed_at = timezone.now()
            obj.published_at = timezone.now()
            obj.save()
            messages.success(
                self.request, "Your registration is ready to be published."
            )
            logger.info(
                f"Verifier {obj.full_id} was marked as ready by {self.request.session['yivi_email']}."
            )
            return redirect(self.get_success_url())

        if obj.approved_scheme_data == obj.new_scheme_data:
            obj.reviewed_accepted = True
            obj.save()
            messages.info(
                self.request, "Your registration didn't change after it was approved."
            )
            logger.info(
                f"Verifier {obj.full_id} was marked as ready for review by {self.request.session['yivi_email']} without changes."
            )
        else:
            obj.reviewed_accepted = None
            obj.reviewed_at = None
            obj.save()
            messages.success(self.request, "Your registration will be reviewed.")
            logger.info(
                f"Verifier {obj.full_id} was marked as ready for review by {self.request.session['yivi_email']}."
            )
        return redirect(self.get_success_url())

    def register_draft(self):
        obj = self.get_object()
        obj.ready = False
        obj.ready_at = None
        obj.reviewed_accepted = None
        obj.save()
        messages.success(self.request, "Your registration is now a draft.")
        logger.info(
            f"Verifier {obj.full_id} was marked as draft by {self.request.session['yivi_email']}."
        )
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "ready_for_review":
            return self.register_ready_for_review()
        elif request.POST.get("action") == "mark_draft":
            return self.register_draft()
        else:
            raise BadRequest("Invalid action")

    def get_success_url(self):
        return self.request.path


class VerifierDeleteView(DeleteView, VerifierPortalView):
    template_name = "verifier/verifier_delete.html"

    def post(self, request, *args, **kwargs):
        if request.POST.get("confirm_delete") != f"delete {self.get_object().full_id}":
            messages.error(self.request, "Invalid confirmation")
            return redirect(request.path)
        logger.info(
            f"Verifier {self.get_object().full_id} was deleted by {self.request.session['yivi_email']}."
        )
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "schememanager:verifier-list",
            kwargs={"org_slug": self.kwargs["org_slug"]},
        )
