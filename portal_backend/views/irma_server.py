import logging
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.request import Request    
from rest_framework import status
from portal_backend.models.models import IrmaServer
from portal_backend.models.model_serializers import IrmaServerSerializer
from portal_backend.swagger_specs.irma_server import irma_server_create_schema
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

logger = logging.getLogger(__name__)

class IrmaServerCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @irma_server_create_schema
    @transaction.atomic
    def post(self, request: Request) -> Response:
        """Create a new Irma Server instance."""

        user_agent = request.headers.get('User-Agent', '')

        if user_agent.lower() != 'irmaserver':
            logger.warning(f'User-Agent is not "irmaserver", but: {user_agent}')
            return Response(
                {"error": "Invalid User-Agent"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = IrmaServerSerializer(data=request.data)
        if serializer.is_valid():
            irma_server = serializer.save()
            return Response(
                IrmaServerSerializer(irma_server).data, status=201
            )
        return Response(serializer.errors, status=400)