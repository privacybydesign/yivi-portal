from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers

from yivi_auth import signals
from yivi_auth.yivi import YiviServer, YiviException

logger = logging.getLogger(__name__)

class YiviSessionProxyStartView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            additional_properties=True
        ),
        responses={200: "Success"}
    )
    def post(self, request):
        """Start a Yivi session as proxy to the Yivi server."""

        logger.info("Starting a Yivi session: " + settings.YIVI_SERVER_TOKEN)

        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            session_request = "{\"@context\":\"https://irma.app/ld/request/disclosure/v2\",\"disclose\":[[[\"pbdf.pbdf.email.email\"],[\"pbdf.sidn-pbdf.email.email\"]]]}"
            response = yivi_server.start_session(request.data)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)

        if response is None:
            raise RuntimeError("Yivi server did not return a response.")

        return Response(data=response)


class YiviSessionProxyResultView(APIView):
    @swagger_auto_schema(
        responses={200: "Success", 400: "Invalid Yivi session token."}
    )
    def get(self, request, token, **kwargs):
        """Get the result of a Yivi session as proxy to the Yivi server."""
        yivi_server = YiviServer(
            settings.YIVI_SERVER_URL, token=settings.YIVI_SERVER_TOKEN
        )

        try:
            yivi_session_result = yivi_server.session_result(token)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)

        # If the Yivi session is done, trigger a signal to notify the application
        if yivi_session_result.get("status") == "DONE":
            return Response(data=yivi_session_result)
