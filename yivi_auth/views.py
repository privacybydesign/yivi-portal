from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import datetime, timezone
import logging
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from drf_yasg import openapi  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore
from portal_backend.models.models import User
from yivi_auth.yivi import YiviServer, YiviException
import time


logger = logging.getLogger(__name__)


class YiviIssueDemosView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, additional_properties=True
        ),
        responses={200: "Success"},
    )
    def post(self, request):
        """Start a Yivi session as proxy to the Yivi server to issue demo credentials."""

        credential: str = request.data.get("credential", None)
        attributes: dict = request.data.get("attributes", None)

        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL,
            token=settings.YIVI_SERVER_TOKEN,
        )
        # UNIX timestamp in the future, 6 months from now
        validity = int(time.time()) + 6 * 30 * 24 * 60 * 60

        try:
            session_request = {
                "@context": "https://irma.app/ld/request/issuance/v2",
                "credentials": [
                    {
                        "credential": credential,
                        "validity": validity,
                        "attributes": attributes,
                    }
                ],
            }
            response = yivi_server.start_session(session_request)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)

        if response is None:
            raise RuntimeError("Yivi server did not return a response.")

        return Response(data=response)


class YiviDemoIssuanceResultView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, yivi_token: str):
        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            result = yivi_server.session_result(yivi_token)
            if result is None:
                return Response(status=400, data="Invalid Yivi token")
            return Response(result, status=200)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # # Add custom claims
        token["email"] = user.email

        db_usr = User.objects.filter(email=user.email).first()
        if db_usr is not None:
            token["role"] = db_usr.role
            organization_slug = list(
                db_usr.organizations.values_list("slug", flat=True)
            )
            token["organizationSlugs"] = organization_slug

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

        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            session_request = {
                "@context": "https://irma.app/ld/request/disclosure/v2",
                "disclose": [
                    [["pbdf.pbdf.email.email"], ["pbdf.sidn-pbdf.email.email"]]
                ],
            }
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

            User = get_user_model()
            user, created = User.objects.get_or_create(username=email, email=email)

            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access_token = str(refresh.access_token)
            response = Response({"access": access_token}, status=200)
            # Cookie expires when refresh token does
            refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
            expires_at = datetime.now(timezone.utc) + refresh_lifetime

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=not settings.DEBUG,  # Set True in production
                samesite="Lax",  # Or "Lax" depending on your app flow
                expires=expires_at,
                path="/",
            )
            return response

        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)


class GetTokenView(APIView):
    pass  # Uses default JWT token response


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Access token",
                examples={
                    "application/json": {
                        "access": "string",
                    }
                },
            ),
            401: "Unauthorized",
        }
    )
    def post(self, request: Request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token missing."}, status=401)
        update_claims = request.data.get("update_claims", False)

        try:
            token = RefreshToken(refresh_token)
            user = get_user_model().objects.get(email=token["email"])

            if update_claims:
                new_tokens = CustomTokenObtainPairSerializer.get_token(user)
                access_token = str(new_tokens.access_token)
                refresh_token = str(new_tokens)
                response = Response({"access": access_token}, status=200)
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    expires=datetime.now(timezone.utc)
                    + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                    path="/",
                )
            else:
                access_token = str(token.access_token)
                response = Response({"access": access_token}, status=200)
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class LogoutView(APIView):
    def post(self, request: Request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({"message": "Successfully logged out"}, status=200)
            response.delete_cookie("refresh_token")
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=400)
