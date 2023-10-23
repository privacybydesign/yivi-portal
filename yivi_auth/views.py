from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from yivi_auth import signals
from yivi_auth.yivi import YiviServer, YiviException


class YiviSessionProxyStartView(APIView):
    def post(self, request, **kwargs):
        """Start a Yivi session as proxy to the Yivi server."""
        yivi_server = YiviServer(
            settings.YIVI_SERVER_HOSTNAME, token=settings.YIVI_SERVER_TOKEN
        )
        try:
            response = yivi_server.start_session(request.data)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)

        # Store the Yivi session token in the Django session
        yivi_session_token = response["token"]
        yivi_sessions = request.session.get("yivi_sessions", []) or []
        yivi_sessions.append(
            {
                "yivi_session_token": yivi_session_token,
                "request": request.data,
                "original_path": request.headers.get("Original-Path", None),
            }
        )

        request.session["yivi_sessions"] = yivi_sessions

        return Response(data=response)


class YiviSessionProxyResultView(APIView):
    def get(self, request, token, **kwargs):
        """Get the result of a Yivi session as proxy to the Yivi server."""
        yivi_server = YiviServer(
            settings.YIVI_SERVER_HOSTNAME, token=settings.YIVI_SERVER_TOKEN
        )

        # Retrieve the original Yivi session from the Django session
        yivi_session = next(
            (
                session
                for session in request.session.get("yivi_sessions", [])
                if session.get("yivi_session_token") == token
            ),
            None,
        )

        # Verify that the Yivi session token is valid
        if yivi_session.get("yivi_session_token") != token:
            return Response(status=400, data="Invalid Yivi session token.")

        try:
            yivi_session_result = yivi_server.session_result(token)
        except YiviException as e:
            return Response(status=e.http_status, data=e.msg)

        # If the Yivi session is done, trigger a signal to notify the application
        if yivi_session_result.get("status") == "DONE":
            signals.yivi_session_done.send_robust(
                self.__class__,
                request=request,
                result=yivi_session_result,
                yivi_session=yivi_session,
            )
        return Response(data=yivi_session_result)
