import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views.generic import (
    TemplateView,
    DetailView,
    UpdateView,
    ListView,
)

from schememanager.forms.organization import *
from schememanager.models.organization import Organization, OrganizationAdmin, KvkEntry
from schememanager.views.login import LoginView

from yivi_auth.signals import yivi_session_done

logger = logging.getLogger()


class RegistrationView(TemplateView):
    template_name = "register.html"

    yivi_request = {
        "@context": "https://irma.app/ld/request/disclosure/v2",
        "disclose": settings.KVK_DISCLOSURE
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["yivi_request"] = self.yivi_request
        context["next_url"] = reverse(
            "schememanager:organization-list"
        )  # For Yivi frontend package, not Django
        return context

    @staticmethod
    def register_new_organization(request, kvk_entry, yivi_email):
        """Try to register a new organization based on the KVK entry that was disclosed."""
        organization = Organization.create_from_kvk_entry(kvk_entry)
        admin = OrganizationAdmin(organization=organization, email=yivi_email)
        admin.full_clean()
        admin.save()
        messages.success(
            request,
            "Organization with kvk number %s was created and you were added as an admin."
            % kvk_entry.kvk_number,
        )
        logger.info(
            f"Organization {organization} was registered by {yivi_email} based on KVK credential."
        )
        return organization

    @staticmethod
    def reregistration_of_organization(request, organization, kvk_entry, yivi_email):
        """Update an existing organization based on the KVK entry that was disclosed."""
        organization.update_from_kvk_entry(kvk_entry)

        logger.info(
            f"Organization {organization} was updated by {yivi_email} based on KVK credential."
        )

        if OrganizationAdmin.objects.filter(
            organization=organization, email=yivi_email
        ).exists():
            messages.warning(
                request,
                "Organization with kvk number %s already exists. You are already an admin."
                % kvk_entry.kvk_number,
            )
        else:
            admin = OrganizationAdmin(organization=organization, email=yivi_email)
            admin.full_clean()
            admin.save()
            messages.warning(
                request,
                "Organization with kvk number %s already exists. You were added as an admin."
                % kvk_entry.kvk_number,
            )
            logger.info(
                f"New admin {yivi_email} was added to organization {organization} after presenting KVK credential"
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
            reference_moment = timezone.datetime.fromisoformat(
                kvk_entry.reference_moment
            )
        except ValueError:
            # Sometimes the reference moment is in a different format
            try:
                reference_moment = timezone.datetime.strptime(
                    kvk_entry.reference_moment, "%Y%m%d%H%M%S%f"
                )
            except ValueError:
                messages.error(
                    request,
                    "The KVK entry could not be processed due to an invalid reference moment.",
                )
                return redirect("schememanager:index")

        if reference_moment.date() < timezone.now().date() - timedelta(days=365):
            # Only allow KVK entries from the last year
            messages.error(
                request,
                "The KVK entry is more than a year old. Please request a more recent KVK credential first.",
            )
            return redirect("schememanager:index")

        if kvk_entry.is_authorized == "Nee":
            # Only allow authorized organizations
            messages.error(
                request,
                "You are not authorized for this organization.",
            )
            return redirect("schememanager:index")

        if kvk_entry.has_restriction == "Ja":
            # Only allow organizations without restrictions
            messages.warning(
                request,
                "You are authorized with restriction. You can proceed, but manual approval is required to complete "
                "the registration.",
            )

        # TODO maybe perform some more checks on the KVK entry: is the organization still active, etc.

        try:
            organization = Organization.objects.get(
                legal_registration_number=kvk_entry.kvk_number
            )
        except Organization.MultipleObjectsReturned:
            raise RuntimeError(
                f"Multiple organizations found for kvk number {kvk_entry.kvk_number}. This should not happen."
            )
        except Organization.DoesNotExist:
            organization = RegistrationView.register_new_organization(
                request, kvk_entry, yivi_email
            )
        else:
            # TODO: actually, we should not allow this. Reregistration should be a separate flow (in which we ask
            #  disclosure of a specific legal number credential!)
            RegistrationView.reregistration_of_organization(
                request, organization, kvk_entry, yivi_email
            )


class OrganizationListView(ListView):
    template_name = "organization/organization_list.html"
    model = Organization
    context_object_name = "organizations"

    def dispatch(self, request, *args, **kwargs):
        if "yivi_email" not in request.session:
            url = reverse("schememanager:login")
            if request.method == "GET":
                url += "?" + urlencode({"next": request.path})
            return redirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user_email = self.request.session.get("yivi_email", None)
        return Organization.objects.filter(admins__email=user_email)


class SingleOrganizationPortalView(DetailView):
    model = Organization
    context_object_name = "organization"
    slug_url_kwarg = "org_slug"

    def dispatch(self, request, *args, **kwargs):
        if "yivi_email" not in request.session:
            url = reverse("schememanager:login")
            if request.method == "GET":
                url += "?" + urlencode({"next": request.path})
            return redirect(url)
        if (
            not self.get_object()
            .admins.filter(email=request.session["yivi_email"])
            .exists()
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class OrganizationLegalPortalView(UpdateView, SingleOrganizationPortalView):
    template_name = "organization/organization_legal.html"
    form_class = OrganizationLegalForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your organization has been updated.")
        logger.info(
            f"Organization {self.get_object()} legal info was updated by {self.request.session['yivi_email']}: {form.changed_data}."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class OrganizationBillingPortalView(UpdateView, SingleOrganizationPortalView):
    template_name = "organization/organization_billing.html"
    form_class = OrganizationBillingForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your organization has been updated.")
        logger.info(
            f"Organization {self.get_object()} billing info was updated by {self.request.session['yivi_email']}: {form.changed_data}."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class OrganizationAdminsView(SingleOrganizationPortalView):
    template_name = "organization/organization_admins.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admins"] = self.get_object().admins.all()
        context["add_admin_form"] = OrganizationAdminForm()
        return context

    def add_admin(self, email):
        if self.get_object().admins.filter(email=email).exists():
            messages.error(
                self.request, "%s is already an admin of your organization." % email
            )
        else:
            form = OrganizationAdminForm({"email": email})
            if not form.is_valid():
                messages.error(
                    self.request,
                    "The email address %s is not a valid email address." % email,
                )
                return redirect(self.get_success_url())
            form.instance.organization = self.get_object()
            instance = form.save()
            messages.success(
                self.request,
                "%s was added as an admin of your organization." % instance.email,
            )
            logger.info(
                f"Admin {instance.email} was added to organization {self.get_object()} by {self.request.session['yivi_email']}."
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
                logger.info(
                    f"Admin {admin.email} left organization {self.get_object()}."
                )
                return redirect("schememanager:organization-list")

            messages.success(
                self.request, "%s was removed from your organization." % admin.email
            )
            logger.info(
                f"Admin {admin.email} was removed from organization {self.get_object()} by {self.request.session['yivi_email']}."
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
