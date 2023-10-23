from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import QuerySet
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.views import View
from django.views.generic import (
    TemplateView,
    DetailView,
    UpdateView,
    ListView,
)
from django.views.generic.detail import SingleObjectMixin

from schememanager import forms
from schememanager.models import (
    Organization,
    OrganizationAdmin,
    KvkEntry,
    Verifier,
    VerifierHostname,
    VerifierSessionRequest,
)
from yivi_auth.signals import yivi_session_done


class IndexView(TemplateView):
    template_name = "index.html"


class LoginView(TemplateView):
    template_name = "login.html"

    yivi_request = {
        "@context": "https://irma.app/ld/request/disclosure/v2",
        "disclose": [[["pbdf.sidn-pbdf.email.email"]]],
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["yivi_request"] = self.yivi_request
        context["next_url"] = self.request.GET.get("next", None) or reverse(
            "schememanager:organization-list"
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        """Redirect after login."""
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin:index")
        if request.session.get("yivi_email", None):
            return redirect("schememanager:portal")
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def yivi_email_disclosure_login(request, email):
        """Log the user in based on the Yivi email disclosure."""
        request.session["yivi_email"] = email

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


class RegistrationView(TemplateView):
    template_name = "register.html"

    yivi_request = {
        "@context": "https://irma.app/ld/request/disclosure/v2",
        "disclose": [
            [
                [
                    "pbdf.signicat.kvkTradeRegister.kvkNumber",
                    "pbdf.signicat.kvkTradeRegister.name",
                    "pbdf.signicat.kvkTradeRegister.tradeNames",
                    "pbdf.signicat.kvkTradeRegister.typeOwner",
                    "pbdf.signicat.kvkTradeRegister.legalEntity",
                    "pbdf.signicat.kvkTradeRegister.address",
                    "pbdf.signicat.kvkTradeRegister.emailAddress",
                    "pbdf.signicat.kvkTradeRegister.phone",
                    "pbdf.signicat.kvkTradeRegister.registrationStart",
                    "pbdf.signicat.kvkTradeRegister.dateDeregistration",
                    "pbdf.signicat.kvkTradeRegister.registrationEnd",
                    "pbdf.signicat.kvkTradeRegister.specialLegalSituation",
                    "pbdf.signicat.kvkTradeRegister.restrictionInLegalAction",
                    "pbdf.signicat.kvkTradeRegister.foreignLegalStatus",
                    "pbdf.signicat.kvkTradeRegister.hasRestriction",
                    "pbdf.signicat.kvkTradeRegister.isAuthorized",
                    "pbdf.signicat.kvkTradeRegister.reason",
                    "pbdf.signicat.kvkTradeRegister.referenceMoment",
                ]
            ],
            [
                [
                    "pbdf.sidn-pbdf.email.email",
                ]
            ],
        ],
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["yivi_request"] = self.yivi_request
        context["next_url"] = reverse("schememanager:organization-list")
        return context

    @staticmethod
    def register_new_organization(request, kvk_entry, yivi_email):
        """Try to register a new organization based on the KVK entry that was disclosed."""
        organization = Organization.create_from_kvk_entry(kvk_entry)
        OrganizationAdmin.objects.create(organization=organization, email=yivi_email)
        messages.success(
            request,
            "Organization with kvk number %s was created and you were added as an admin."
            % kvk_entry.kvk_number,
        )

    @staticmethod
    def reregistration_of_organization(request, organization, kvk_entry, yivi_email):
        """Update an existing organization based on the KVK entry that was disclosed."""
        if OrganizationAdmin.objects.filter(
            organization=organization, email=yivi_email
        ).exists():
            messages.warning(
                request,
                "Organization with kvk number %s already exists. You are already an admin."
                % kvk_entry.kvk_number,
            )
        else:
            OrganizationAdmin.objects.create(
                organization=organization, email=yivi_email
            )
            messages.warning(
                request,
                "Organization with kvk number %s already exists. You were added as an admin."
                % kvk_entry.kvk_number,
            )

    @staticmethod
    @receiver(yivi_session_done)
    def yivi_session_done_handler(sender, request, result, yivi_session, **kwargs):
        if not (
            yivi_session["original_path"] == "/register/"
            and yivi_session["request"] == RegistrationView.yivi_request
        ):
            return

        yivi_email = result["disclosed"][1][0]["rawvalue"]
        LoginView.yivi_email_disclosure_login(request, yivi_email)

        kvk_entry = KvkEntry(
            kvk_number=result["disclosed"][0][0]["rawvalue"],
            name=result["disclosed"][0][1]["rawvalue"],
            trade_names=result["disclosed"][0][2]["rawvalue"],
            type_owner=result["disclosed"][0][3]["rawvalue"],
            legal_entity=result["disclosed"][0][4]["rawvalue"],
            address=result["disclosed"][0][5]["rawvalue"],
            email=result["disclosed"][0][6]["rawvalue"],
            phone=result["disclosed"][0][7]["rawvalue"],
            registration_start=result["disclosed"][0][8]["rawvalue"],
            date_deregistration=result["disclosed"][0][9]["rawvalue"],
            registration_end=result["disclosed"][0][10]["rawvalue"],
            special_legal_situation=result["disclosed"][0][11]["rawvalue"],
            restriction_in_legal_action=result["disclosed"][0][12]["rawvalue"],
            foreign_legal_status=result["disclosed"][0][13]["rawvalue"],
            has_restriction=result["disclosed"][0][14]["rawvalue"],
            is_authorized=result["disclosed"][0][15]["rawvalue"],
            reason=result["disclosed"][0][16]["rawvalue"],
            reference_moment=result["disclosed"][0][17]["rawvalue"],
        )

        try:
            organization = Organization.objects.get(kvk_number=kvk_entry.kvk_number)
        except Organization.MultipleObjectsReturned:
            raise RuntimeError(
                f"Multiple organizations found for kvk number {kvk_entry.kvk_number}. This should not happen."
            )
        except Organization.DoesNotExist:
            RegistrationView.register_new_organization(request, kvk_entry, yivi_email)
        else:
            RegistrationView.reregistration_of_organization(
                request, organization, kvk_entry, yivi_email
            )


def get_accessible_organizations(request) -> QuerySet[Organization]:
    user_email = request.session.get("yivi_email", None)
    return Organization.objects.filter(admins__email=user_email)


class OrganizationListView(ListView):
    template_name = "portal/organization_list.html"
    model = Organization
    context_object_name = "organizations"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accessible_organizations"] = get_accessible_organizations(self.request)
        return context

    def dispatch(self, request, *args, **kwargs):
        if "yivi_email" not in request.session:
            return redirect("schememanager:login")  # TODO add next-url
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_accessible_organizations(self.request)


class SingleOrganizationPortalView(SingleObjectMixin, View):
    model = Organization
    context_object_name = "organization"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accessible_organizations"] = get_accessible_organizations(self.request)
        return context

    def dispatch(self, request, *args, **kwargs):
        if "yivi_email" not in request.session:
            return redirect("schememanager:login")  # TODO add next-url
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj not in get_accessible_organizations(self.request):
            raise PermissionDenied()
        return obj


class OrganizationPortalView(UpdateView, SingleOrganizationPortalView):
    template_name = "portal/organization.html"
    form_class = forms.OrganizationForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your organization has been updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class OrganizationAdminsView(DetailView, SingleOrganizationPortalView):
    template_name = "portal/organization_admins.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admins"] = self.get_object().admins.all()
        context["add_admin_form"] = forms.OrganizationAdminForm()
        return context

    def add_admin(self, email):
        if self.get_object().admins.filter(email=email).exists():
            messages.error(
                self.request, "%s is already an admin of your organization." % email
            )
        else:
            instance = OrganizationAdmin.objects.create(
                organization=self.get_object(), email=email
            )
            messages.success(
                self.request,
                "%s was added as an admin of your organization." % instance.email,
            )
        return redirect(self.get_success_url())

    def remove_admin(self, email):
        admins = self.get_object().admins
        if admins.count() == 1 and admins.filter(email=email).exists():
            messages.error(
                self.request, "Your organization must have at least one admin."
            )
        else:
            admin = admins.get(email=email)
            admin.delete()

            if email == self.request.session.get("yivi_email", None):
                messages.success(
                    self.request, "You have successfully left the organization."
                )
                return redirect("schememanager:organization-list")

            messages.success(
                self.request, "%s was removed from your organization." % admin.email
            )
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "remove":
            return self.remove_admin(request.POST.get("email"))
        elif request.POST.get("action") == "add":
            return self.add_admin(request.POST.get("email"))
        else:
            raise RuntimeError("Invalid action")

    def get_success_url(self):
        return self.request.path


class SingleVerifierPortalView(SingleOrganizationPortalView):
    def get_organization(self):
        return super().get_object()

    def get_object(self, queryset=None):
        organization = super().get_object(queryset=queryset)
        try:
            return organization.verifier
        except Verifier.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.get_organization()
        context["verifier"] = self.get_object()
        return context


class VerifierPortalView(UpdateView, SingleVerifierPortalView):
    template_name = "portal/verifier.html"
    form_class = forms.VerifierForm

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.organization = self.get_organization()
        form.save()
        messages.success(self.request, "Your verifier has been updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class VerifierHostnamesView(DetailView, SingleVerifierPortalView):
    template_name = "portal/verifier_hostnames.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hostnames"] = self.get_object().hostnames.all()
        context["add_hostname_form"] = forms.VerifierHostnameForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object():
            messages.error(self.request, "You must first register as a verifier.")
            return redirect("schememanager:verifier-portal", slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def add_hostname(self, hostname):
        if self.get_object().hostnames.filter(hostname=hostname).exists():
            messages.error(
                self.request, "%s is already registered as hostname." % hostname
            )
        else:
            try:
                instance = VerifierHostname.objects.create(
                    verifier=self.get_object(), hostname=hostname
                )
                messages.info(
                    self.request,
                    "%s was added as hostname. Awaiting verification."
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
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "remove":
            return self.remove_hostname(request.POST.get("hostname"))
        elif request.POST.get("action") == "add":
            return self.add_hostname(request.POST.get("hostname"))
        else:
            raise RuntimeError("Invalid action")

    def get_success_url(self):
        return self.request.path


class VerifierSessionRequestsView(DetailView, SingleVerifierPortalView):
    template_name = "portal/verifier_session_requests.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["session_requests"] = self.get_object().session_requests.all()
        context["add_session_request_form"] = forms.VerifierSessionRequestAddForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object():
            messages.error(self.request, "You must first register as a verifier.")
            return redirect("schememanager:verifier-portal", slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def add_session_request(self, condiscon):
        instance = VerifierSessionRequest.objects.create(
            verifier=self.get_object(), condiscon=condiscon
        )
        messages.info(self.request, "Session request was added.")
        return redirect(self.get_success_url())

    def update_session_request(self, session_request, attribute_reasons):
        for attribute in session_request.attributes.all():
            attribute.reason_en = attribute_reasons[attribute.attribute_id]["en"]
            attribute.reason_nl = attribute_reasons[attribute.attribute_id]["nl"]
            attribute.save()
        messages.success(self.request, "Session request was updated.")
        return redirect(self.get_success_url())

    def remove_session_request(self, session_request_id):
        self.get_object().session_requests.get(id=session_request_id).delete()
        messages.success(self.request, "Session request was removed.")
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "remove":
            return self.remove_session_request(request.POST.get("session_request"))
        elif request.POST.get("action") == "update":
            session_request_id = request.POST.get("session_request")
            session_request = self.get_object().session_requests.get(
                id=session_request_id
            )
            attribute_reasons = {
                attribute_id: {
                    "en": request.POST["reason-en-" + attribute_id],
                    "nl": request.POST["reason-nl-" + attribute_id],
                }
                for attribute_id in session_request.condiscon_attributes
            }
            return self.update_session_request(session_request, attribute_reasons)
        elif request.POST.get("action") == "add":
            return self.add_session_request(request.POST.get("condiscon"))
        else:
            raise RuntimeError("Invalid action")

    def get_success_url(self):
        return self.request.path


class IssuerPortalView(SingleOrganizationPortalView):
    template_name = "portal/issuer.html"

    def dispatch(self, request, *args, **kwargs):
        return redirect("schememanager:organization-portal", slug=kwargs["slug"])
