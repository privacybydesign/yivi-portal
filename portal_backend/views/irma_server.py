from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.request import Request    
from rest_framework import status
from portal_backend.models.models import IrmaServer
from portal_backend.models.model_serializers import IrmaServerSerializer
from portal_backend.swagger_specs.irma_server import irma_server_create_schema, irma_server_update_schema, irma_server_delete_schema
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction


class IrmaServerCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @irma_server_create_schema
    @transaction.atomic
    def post(self, request: Request) -> Response:
        """Create a new Irma Server instance."""
        serializer = IrmaServerSerializer(data=request.data)
        if serializer.is_valid():
            irma_server = serializer.save()
            return Response(
                IrmaServerSerializer(irma_server).data, status=201
            )
        return Response(serializer.errors, status=400)

class IrmaServerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve an Irma Server instance by its primary key."""
        try:
            irma_server = IrmaServer.objects.get(pk=pk)
        except IrmaServer.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        serializer = IrmaServerSerializer(irma_server)
        return Response(serializer.data, status=200)
    
class IrmaServerListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """List all Irma Server instances."""
        irma_servers = IrmaServer.objects.all()
        serializer = IrmaServerSerializer(irma_servers, many=True)
        return Response(serializer.data, status=200)
    
class IrmaServerUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @irma_server_update_schema
    @transaction.atomic
    def put(self, request: Request, pk: int) -> Response:
        """Update an existing Irma Server instance."""
        try:
            irma_server = IrmaServer.objects.get(pk=pk)
        except IrmaServer.DoesNotExist:
            return Response({"detail": "Irma Server not found."}, status=404)
        serializer = IrmaServerSerializer(irma_server, data=request.data, partial=True)
        if serializer.is_valid():
            irma_server = serializer.save()
            return Response(
                IrmaServerSerializer(irma_server).data, status=200
            )
        return Response(serializer.errors, status=400)
    
class IrmaServerDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @irma_server_delete_schema
    def delete(self, request: Request, pk: int) -> Response:
        """Delete an Irma Server instance."""
        try:
            irma_server = IrmaServer.objects.get(pk=pk)
        except IrmaServer.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        deleted = irma_server.delete()
        if deleted:
            return Response(
                {"message": "Irma server deleted successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Irma server could not be deleted."},
                status=status.HTTP_404_NOT_FOUND,
            )