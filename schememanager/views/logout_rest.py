from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutRestView(APIView):
     """REST API View for handling logout and blacklisting the refresh token."""
     
     def post(self, request):
        try:  
            refreshToken = request.data.get("refresh")
            if not refreshToken:
                return Response({"error": "refresh token is invalid"}, status=status.HTTP_400_BAD_REQUEST)

            #blacklist the refresh token 
            refreshToken = RefreshToken(refreshToken)
            refreshToken.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Logout Failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)