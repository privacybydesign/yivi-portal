from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models.models import *
from django.shortcuts import get_object_or_404
from ..models.model_serializers import *
from rest_framework import permissions
from django.utils import timezone
from django.db import transaction



class RelyingPartyListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success", 404: "Not Found"}
    )
    def get(self, request, environment):
        """Gets details of a specific attestation provider by ID."""
        relying_party = RelyingParty.objects.get(yivi_tme__environment=environment)
        serializer = RelyingPartySerializer(relying_party)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RelyingPartyRegisterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def make_condiscon_from_attributes(self, attributes_data):
        """
        Generate a condiscon JSON structure from attribute data
        """
        condiscon_json = {
            "@context": "https://irma.app/ld/request/disclosure/v2",
            "disclose": [[]] 
        }
        
        credential_attributes = {}
        for attr in attributes_data:
            credential_attribute = CredentialAttribute.objects.get(id=attr['credential_attribute_id'])
            credential_id = credential_attribute.credential.id
            
            if credential_id not in credential_attributes:
                credential_attributes[credential_id] = []
            
            credential_attributes[credential_id].append(credential_attribute.name)
        
        for credential_id, attribute_list in credential_attributes.items():
            condiscon_json['disclose'][0].append(attribute_list)
        
        return condiscon_json

    @swagger_auto_schema(
        responses={201: "Created", 404: "Not Found", 400: "Bad Request", 401: "Unauthorized"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['hostname', 'trust_model_env', 'attributes', 'context_description_en', 'context_description_nl'],
            properties={
                'hostname': openapi.Schema(type=openapi.TYPE_STRING),
                'trust_model_env': openapi.Schema(type=openapi.TYPE_STRING),
                'context_description_en': openapi.Schema(type=openapi.TYPE_STRING),
                'context_description_nl': openapi.Schema(type=openapi.TYPE_STRING),
                'attributes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'credential_attribute_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'reason_en': openapi.Schema(type=openapi.TYPE_STRING),
                            'reason_nl': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                ),
            }
        )
    )
    @transaction.atomic  # Rollback if any part of the transaction fails
    def post(self, request, pk):
        """Registers a new relying party, given the user is authenticated and is the maintainer of the org with same pk as in the URL"""

        email_in_token = request.user.email
        user_obj = get_object_or_404(User, email=email_in_token)
        user_org_id = user_obj.organization.id

        if str(user_org_id) != str(pk):
            return Response(
                {"error": "Unauthorized: User does not belong to this organization"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user_obj.role not in ["maintainer", "admin"]:
            return Response(
                {"error": "Unauthorized: User does not have required permissions"},
                status=status.HTTP_403_FORBIDDEN
            )

        if RelyingParty.objects.filter(organization__id=pk).exists():
            return Response(
                {"error": "An organization can only register as a Relying Party once."},
                status=status.HTTP_400_BAD_REQUEST
            )

        yivi_tme = get_object_or_404(YiviTrustModelEnv, environment=request.data.get("trust_model_env"))

        hostname_text = request.data.get("hostname")
        hostname, created = RelyingPartyHostname.objects.get_or_create(
            hostname=hostname_text,
            defaults={
                'dns_challenge': f'"yivi_verifier_challenge={uuid.uuid4().hex}"',  # Use random string for now
                'dns_challenge_created_at': timezone.now(),
                'dns_challenge_verified': False
            }
        )

        app_status_data = {
            "ready": False,
            "reviewed_accepted": False
        }

        serializer = ApplicationStatusSerializer(data=app_status_data)
        if serializer.is_valid():
            app_status = serializer.save()  
        else:
            return Response(
                {"error": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process attributes
        attributes_data = request.data.get("attributes", [])
        context_en = request.data.get("context_description_en")
        context_nl = request.data.get("context_description_nl")

        try:
            condiscon_json = self.make_condiscon_from_attributes(attributes_data)

            # Create condiscon
            condiscon = Condiscon(
                condiscon=condiscon_json,
                context_description_en=context_en,
                context_description_nl=context_nl
            )
            condiscon.full_clean()
            condiscon.save()

            # Get organization
            organization = get_object_or_404(Organization, id=pk)

            # Create relying party
            relying_party = RelyingParty(
                yivi_tme=yivi_tme,
                organization=organization,
                status=app_status,
                hostname=hostname,
                condiscon=condiscon
            )
            relying_party.full_clean()
            relying_party.save()

            # Create condiscon attributes
            for attr_data in attributes_data:
                credential_attribute = get_object_or_404(
                    CredentialAttribute, 
                    id=attr_data['credential_attribute_id']
                )

                condiscon_attr = CondisconAttribute(
                    credential_attribute=credential_attribute,
                    condiscon=condiscon,
                    reason_en=attr_data['reason_en'],
                    reason_nl=attr_data['reason_nl']
                )
                condiscon_attr.full_clean()
                condiscon_attr.save()

            return Response({
                "id": str(relying_party.id),
                "message": "Relying party registration successful",
                "dns_challenge": hostname.dns_challenge,
                "hostname": hostname.hostname,
                "status": {
                    "ready": app_status.ready,
                    "reviewed_accepted": app_status.reviewed_accepted
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error registering relying party: {e}")
            return Response(
                {"error": f"Failed to register relying party: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

