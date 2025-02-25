from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from ..models.models import *
from django.shortcuts import get_object_or_404
from ..models.model_serializers import *

from rest_framework import permissions

class TrustModelListAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        responses={200: "Success"}
    )
    def get(self, request):
        """Gets a list of trust models."""
        trust_models = TrustModel.objects.all()
        serializer = TrustModelSerializer(trust_models, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class TrustModelDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success",
                   404: "Not found"}
    )
    def get(self,request,name , environment=None, entity=None):
        """gets yivi's details , list of attestation providers and relying parties"""
        if name == "yivi":
            if environment:
                yivi_trust_model = get_object_or_404(YiviTrustModelEnv,environment=environment)
                serializer = YiviTrustModelSerializer(yivi_trust_model)
                if entity=="attestation-providers":
                    attestation_provider = AttestationProvider.objects.all()
                    serializer = AttestationProviderSerializer(attestation_provider, many=True)
                    Response(serializer.data,status=status.HTTP_200_OK)

                elif entity=="relying-parties":
                    relying_party = RelyingParty.objects.all()
                    serializer = RelyingPartySerializer(relying_party, many=True)
                    return Response(serializer.data,status=status.HTTP_200_OK)


            else:
                yivi_trust_model = YiviTrustModelEnv.objects.all()
                serializer = YiviTrustModelSerializer(yivi_trust_model, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)

        trust_model = get_object_or_404(TrustModel, name=name)
        serializer = TrustModelSerializer(trust_model)
        return Response(serializer.data,status=status.HTTP_200_OK)
