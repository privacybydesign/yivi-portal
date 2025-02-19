from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
import logging

class CreateOrganizationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    domain = serializers.CharField(max_length=200)
    
class GetOrganizationSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    domain = serializers.CharField(max_length=200)
    logo = serializers.CharField(max_length=200)

logger = logging.getLogger(__name__)

class OrganizationsRestView(APIView):
    
    @swagger_auto_schema(
        request_body=CreateOrganizationSerializer,
        responses={200: "Success"}
    )
    def post(self, request):
        """Creates an organization."""
        return Response(status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        responses={200: GetOrganizationSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        
        logger.info(f"User {user.email} is getting organizations.")
        
        """Gets a list of organizations."""
        organizations = [
            {
                "id": "nijmegen",
                "name": "Gemeente Nijmegen",
                "logo": "/logos/nijmegen.jpg",
                "domain": "nijmegen.nl",
                "issuer": { "status": "Active", "color": "green" },
                "verifier": { "status": "Inactive", "color": "red" },
            },
            {
                "id": "pubhubs",
                "name": "PubHubs",
                "domain": "pubhubs.net",
                "logo": "/logos/pubhubs.png",
                "issuer": { "status": "Inactive", "color": "red" },
                "verifier": { "status": "Active", "color": "green" },
            },
            {
                "id": "minvws",
                "name": "Ministerie van Volksgezondheid Welzijn en Sport",
                "domain": "orgc.org",
                "logo": "/logos/minvws.jpg",
                "issuer": { "status": "Pending", "color": "yellow" },
                "verifier": { "status": "Active", "color": "green" },
            },
        ]
        return Response(organizations)