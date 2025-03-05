from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from ..models.model_serializers import OrganizationSerializer
from ..models.models import Organization
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404


class OrganizationListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request):
        """Get all registered organizations"""
        orgs = Organization.objects.filter(is_verified=True)
        paginator = LimitOffsetPagination()  
        paginator.default_limit = 10  
        result_page = paginator.paginate_queryset(orgs, request)
        serializer = OrganizationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=OrganizationSerializer,
        responses={201: "Success"
                ,400: "Bad Request"}
    )
    def post(self, request):
        """Creates an organization."""
        serializer = OrganizationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        organization = serializer.save()
        return Response({"id":organization.id},status=status.HTTP_201_CREATED)
    
class OrganizationDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

        
    @swagger_auto_schema(
        responses={200: "Success"}
    )
    def get(self, pk):
        """Get organization by uuid"""
        org = Organization.objects.get(pk=pk)
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)
    
    @swagger_auto_schema(
    request_body=OrganizationSerializer,
    responses={201: "Success"
            ,400: "Bad Request"
            ,404: "Not Found"})
    def patch(self, request, pk):
        """Updates an organization, given the uuid."""
        organization = get_object_or_404(Organization, pk=pk)
        serializer = OrganizationSerializer(organization, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"Your Organization registration was updated.",serializer.data},status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_200_OK)