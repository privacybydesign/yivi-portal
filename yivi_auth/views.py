from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import logging
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from drf_yasg import openapi  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore
from portal_backend.models.models import User
from yivi_auth.yivi import YiviServer, YiviException

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        logger.info("User with email: " + user.email + " logged in.")
        # # Add custom claims
        token["email"] = user.email
        
        db_usr = User.objects.filter(email=user.email).first()
        if db_usr is not None:
            token['role'] = db_usr.role
            token['organizationId'] = str(db_usr.organization.id)

        return token


class YiviSessionProxyStartView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, additional_properties=True
        ),
        responses={200: "Success"},
    )
    def post(self, request):
        """Start a Yivi session as proxy to the Yivi server."""

        logger.info("Starting a Yivi session: " + settings.YIVI_SERVER_TOKEN)

        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            session_request = {
                "@context":"https://irma.app/ld/request/disclosure/v2",
                "disclose":[[["pbdf.pbdf.email.email"],["pbdf.sidn-pbdf.email.email"]]]}
            response = yivi_server.start_session(session_request)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)

        if response is None:
            raise RuntimeError("Yivi server did not return a response.")

        return Response(data=response)


class YiviSessionProxyResultView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(responses={200: "Success", 400: "Invalid Yivi session token."})
    def get(self, request, yivi_token: str):
        """Get the result of a Yivi session as proxy to the Yivi server."""
        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )

        try:
            yivi_session_result = yivi_server.session_result(yivi_token)
            if yivi_session_result is None:
                return Response(status=400, data="Invalid Yivi session token.")

            email = yivi_session_result.get("disclosed")[0][0]["rawvalue"]
            logger.info("Yivi session result received for:  " + email)

            User = get_user_model()
            user, created = User.objects.get_or_create(username=email, email=email)

            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access_token = str(refresh.access_token)
            return Response(
                {"refresh": str(refresh), "access": access_token}, status=200
            )
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)


class GetTokenView(APIView):
    pass  # Uses default JWT token response


class RefreshTokenView(APIView):
    pass  # Uses default JWT token response


class LogoutView(APIView):
    def post(request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
