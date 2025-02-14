from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from schememanager.models.organization import Organization, OrganizationAdmin, KvkEntry
from schememanager.forms.organization import OrganizationAdminForm


class RegistrationRestView(APIView):
    """REST API View for handling organization registration and re-registration based on KVK disclosure."""

    def post(self, request):
        """Handle KVK disclosure registration request."""
        data = request.data  

        kvk_data = data.get("kvk_entry")
        yivi_email = data.get("yivi_email")

        if not kvk_data or not yivi_email:
            return Response({"error": "KVK entry and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            kvk_entry = self.parse_kvk_entry(kvk_data)
            self.validate_kvk_entry(kvk_entry)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(legal_registration_number=kvk_entry.kvk_number)
        except Organization.DoesNotExist:
            organization = self.register_new_organization(kvk_entry, yivi_email)
            return Response({"message": "Organization created successfully.", "organization_id": organization.id}, status=status.HTTP_201_CREATED)
        except Organization.MultipleObjectsReturned:
            return Response({"error": f"Multiple organizations found for that KVK number."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        self.reregistration_of_organization(organization, kvk_entry, yivi_email)
        return Response({"message": "Organization updated successfully.", "organization_id": organization.id}, status=status.HTTP_200_OK)

    def parse_kvk_entry(self, kvk_data):
        """Convert the KVK entry data from JSON to a KvkEntry object."""
        try:
            return KvkEntry(
                kvk_number=kvk_data["kvk_number"],
                name=kvk_data["name"],
                trade_names=kvk_data["trade_names"],
                type_owner=kvk_data["type_owner"],
                legal_entity=kvk_data["legal_entity"],
                address=kvk_data["address"],
                email=kvk_data["email"],
                phone=kvk_data["phone"],
                registration_start=kvk_data["registration_start"],
                date_deregistration=kvk_data["date_deregistration"],
                registration_end=kvk_data["registration_end"],
                special_legal_situation=kvk_data["special_legal_situation"],
                restriction_in_legal_action=kvk_data["restriction_in_legal_action"],
                foreign_legal_status=kvk_data["foreign_legal_status"],
                has_restriction=kvk_data["has_restriction"],
                is_authorized=kvk_data["is_authorized"],
                reason=kvk_data["reason"],
                reference_moment=kvk_data["reference_moment"],
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")

    def validate_kvk_entry(self, kvk_entry):
        """Validate the KVK entry for registration rules."""
        try:
            reference_moment = timezone.datetime.fromisoformat(kvk_entry.reference_moment)
        except ValueError:
            raise ValueError("Invalid reference moment format.")

        if reference_moment.date() < timezone.now().date() - timedelta(days=365):
            raise ValueError("The KVK entry is more than a year old. Please provide a more recent KVK credential.")

        if kvk_entry.is_authorized == "Nee":
            raise ValueError("You are not authorized for this organization.")

        if kvk_entry.has_restriction == "Ja":
            raise ValueError("You are authorized with restriction. Manual approval is required.")

    def register_new_organization(self, kvk_entry, yivi_email):
        """Register a new organization."""
        organization = Organization.create_from_kvk_entry(kvk_entry)
        admin = OrganizationAdmin(organization=organization, email=yivi_email)
        admin.full_clean()
        admin.save()
        return organization

    def reregistration_of_organization(self, organization, kvk_entry, yivi_email):
        """Re-register an existing organization."""
        organization.update_from_kvk_entry(kvk_entry)
        if not OrganizationAdmin.objects.filter(organization=organization, email=yivi_email).exists():
            admin = OrganizationAdmin(organization=organization, email=yivi_email)
            admin.full_clean()
            admin.save()
