from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models.models import *
from ..dns_verification import generate_dns_challenge
from django.shortcuts import get_object_or_404
from ..models.model_serializers import *
from rest_framework import permissions
from django.utils import timezone
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..dns_verification import generate_dns_challenge
from .helpers import IsMaintainer, BelongsToOrganization


def check_existing_hostname(request):
    request_hostname = request.data.get("hostname")
    
    if RelyingPartyHostname.objects.filter(hostname=request_hostname).exists():
        return Response(
            {"error": "This hostname is already registered by another relying party"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return None
    
class RelyingPartyListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success", 404: "Not Found"}
    )
    def get(self, request, name: str, environment: str):
        """Gets details of a specific attestation provider by ID."""
        relying_party = get_object_or_404(RelyingParty, yivi_tme__trust_model__name=name, yivi_tme__environment=environment)
        serializer = RelyingPartySerializer(relying_party)
        return Response(data=serializer, status=status.HTTP_200_OK)


class RelyingPartyRegisterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, BelongsToOrganization, IsMaintainer]

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
            credential_attribute = CredentialAttribute.objects.get(credential__credential_tag=attr['credential_attribute_tag'], name=attr['credential_attribute_name'])
            credential_id = credential_attribute.credential.id
            
            if credential_id not in credential_attributes:
                credential_attributes[credential_id] = []
            
            credential_attributes[credential_id].append(credential_attribute.name)
        
        for credential_id, attribute_list in credential_attributes.items():
            condiscon_json['disclose'][0].append(attribute_list)
        
        return condiscon_json
    

    
    def save_rp(self, request, org_pk):
            yivi_tme = get_object_or_404(YiviTrustModelEnv, environment=request.data.get("trust_model_env"))
            organization = get_object_or_404(Organization, id=org_pk)
            relying_party = RelyingParty(
                yivi_tme=yivi_tme,
                organization=organization,
            )
            relying_party.full_clean()
            relying_party.save()
            return relying_party

    def save_hostname(self, request, rp):
        hostname_text = request.data.get("hostname")
        hostname, _ = RelyingPartyHostname.objects.get_or_create(
            relying_party=rp,
            hostname=hostname_text,
            defaults={
                'dns_challenge': generate_dns_challenge(),
                'dns_challenge_created_at': timezone.now(),
                'dns_challenge_verified': False
            })
        hostname.full_clean()
        hostname.save()
        return hostname
        

    def save_condiscon(self,request, attributes_data , rp):
        condiscon_json = self.make_condiscon_from_attributes(attributes_data)
        context_en = request.data.get("context_description_en")
        context_nl = request.data.get("context_description_nl")
        condiscon = Condiscon(
            condiscon=condiscon_json,
            context_description_en=context_en,
            context_description_nl=context_nl,
            relying_party=rp,

        )
        condiscon.full_clean()
        condiscon.save()
        return condiscon
    
    def create_initial_status(self,rp):
        status = Status(
            relying_party=rp,
        )
        status.save()
        return status

    def save_condiscon_attributes(self,condiscon, attributes_data):
            for attr_data in attributes_data:
                credential_attribute = get_object_or_404(
                    CredentialAttribute, 
                    credential__credential_tag=attr_data['credential_attribute_tag'],
                    name=attr_data['credential_attribute_name']
                )

                condiscon_attr = CondisconAttribute(
                    credential_attribute=credential_attribute,
                    condiscon=condiscon,
                    reason_en=attr_data['reason_en'],
                    reason_nl=attr_data['reason_nl']
                )
                condiscon_attr.full_clean()
                condiscon_attr.save()

    def check_existing_rp(self,request,org_pk):

        if RelyingParty.objects.filter(organization__id=org_pk).exists():
            return Response(
                {"error": "The organization already has a relying party registered"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return None
            

            

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

    @transaction.atomic  # rollback if any part of the transaction fails
    def post(self, request, pk):
        """Registers a new relying party, given the user is authenticated and is the maintainer of the org with same pk as in the URL"""

        existing_rp = self.check_existing_rp(request, pk)
        if existing_rp:
            return existing_rp
        existing_hostname = check_existing_hostname(request)
        if existing_hostname:
            return existing_hostname
        
        relying_party = self.save_rp(request, pk)
        rp_status = self.create_initial_status(relying_party)
        hostname = self.save_hostname(request, relying_party)
        attributes_data = request.data.get("attributes", [])
        condiscon = self.save_condiscon(request, attributes_data, relying_party)
        self.save_condiscon_attributes(condiscon, attributes_data)


        return Response({
            "id": str(relying_party.id),
            "message": "Relying party registration successful",
            "dns_challenge": hostname.dns_challenge,
            "hostname": hostname.hostname,
            "current_status": rp_status.rp_status.label
        }, status=status.HTTP_201_CREATED)
        
    def patch(self, request, pk):
        """Mark a relying party as ready, or update its details"""
        relying_party = get_object_or_404(RelyingParty, organization__id=pk)
        response_message = "Relying party updated successfully"
        response_data = {"id": str(relying_party.id)}
        
        if request.data.get("hostname") is not None:
            hostname_text = request.data.get("hostname")
            
            existing_hostname = check_existing_hostname(request)
            if existing_hostname:
                return existing_hostname
                
            hostname_obj = get_object_or_404(RelyingPartyHostname, relying_party=relying_party)
            
            if hostname_obj.hostname != hostname_text:
                hostname_obj.hostname = hostname_text
                hostname_obj.dns_challenge = generate_dns_challenge()
                hostname_obj.dns_challenge_created_at = timezone.now()
                hostname_obj.dns_challenge_verified = False
                hostname_obj.dns_challenge_verified_at = None
                hostname_obj.save()
                response_data["hostname"] = hostname_obj.hostname    # add hostname dns challenge to response
                response_data["dns_challenge"] = hostname_obj.dns_challenge
                response_message += ". Hostname updated. Please update your DNS record with the new challenge."
            else:
                hostname_obj.save()
            
        if request.data.get("context_description_en") is not None or request.data.get("context_description_nl") is not None:
            condiscon = get_object_or_404(Condiscon, relying_party=relying_party)
            if request.data.get("context_description_en") is not None:
                condiscon.context_description_en = request.data.get("context_description_en")
            if request.data.get("context_description_nl") is not None:
                condiscon.context_description_nl = request.data.get("context_description_nl")
            condiscon.save()

        if request.data.get("attributes") is not None:
            attributes_data = request.data.get("attributes")
            condiscon = get_object_or_404(Condiscon, relying_party=relying_party)
            CondisconAttribute.objects.filter(condiscon=condiscon).delete()
            self.save_condiscon_attributes(condiscon, attributes_data)
            condiscon.condiscon = self.make_condiscon_from_attributes(attributes_data)
            condiscon.save()

        if request.data.get("trust_model_env") is not None:
            yivi_tme = get_object_or_404(YiviTrustModelEnv, environment=request.data.get("trust_model_env"))
            relying_party.yivi_tme = yivi_tme
            relying_party.save()

        if "ready" in request.data:
            rp_status = Status.objects.get(relying_party=relying_party)
            rp_status.ready = request.data.get("ready")
            rp_status.ready_at = timezone.now() if request.data.get("ready") else None
            rp_status.save()

        elif any(field in request.data for field in ["hostname", "context_description_en", "context_description_nl", "attributes", "trust_model_env"]): # if any of these fields are updated, set ready to False. User must explicitly set ready to make status PENDING FOR REVIEW
            rp_status = Status.objects.get(relying_party=relying_party)
            rp_status.ready = False
            rp_status.save()

        response_data["message"] = response_message
        return Response(response_data, status=status.HTTP_200_OK)

class RelyingPartyHostnameStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, BelongsToOrganization, IsMaintainer]
        
    @swagger_auto_schema(
        responses={200: "Success"})
    
    def get(self, request, slug):
        """Get status of DNS verification for a hostname"""
        relying_party = get_object_or_404(RelyingParty, organization__slug=slug)
        hostname = get_object_or_404(RelyingPartyHostname, relying_party=relying_party)
        
        return Response({
            "hostname": hostname.hostname,
            "dns_challenge": hostname.dns_challenge,
            "manually_verified": hostname.manually_verified, # hostname can be manually set as verified by admins in admin panel
            "dns_challenge_verified": hostname.dns_challenge_verified,
            "dns_challenge_verified_at": hostname.dns_challenge_verified_at,
            "dns_challenge_invalidated_at": hostname.dns_challenge_invalidated_at
        })
    
class RelyingPartyRegistrationStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, BelongsToOrganization, IsMaintainer]
    
    @swagger_auto_schema(
        responses={200: "Success"})
    
    def get(self, request, slug):
        """Get status of relying party registration"""
        relying_party = get_object_or_404(RelyingParty, organization__slug=slug)
        status = get_object_or_404(Status, relying_party=relying_party)
        
        return Response({
            "current_status": status.rp_status.label,
            "ready": status.ready,
            "ready_at": status.ready_at
        })  
    