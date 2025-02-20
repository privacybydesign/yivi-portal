from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

class TrustModelRestView(APIView):
    
    @swagger_auto_schema(
        responses={200: "Success"}
    )
    def get(self, request):
        """Gets a list of trust models."""
        trust_models = [{
            "id": "yivi",
            "name": "Yivi Trust Model",
            "description": "Yivi Trust Model",
        }]
        return Response(trust_models)
    