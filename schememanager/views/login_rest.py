from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, login
from django.contrib.sessions.models import Session
import logging 
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger()


class LoginRestView(TemplateView):
    """REST API View for handling Yivi email login."""
    template_name = "login.html"

    def post(self, request):
        """Handle Yivi email disclosure login."""
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_model = get_user_model()
        try: 
            user = user_model.objects.get(email=email)

        except user_model.DoesNotExist:
            return Response({"error: User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except user_model.MultipleObjectsReturned:
            return Response({"error": "Multiple users found with this email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Generate JWT Token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
                "refresh": str(refresh),
                "access": access_token,
                "email": email           
                }, status=200)
        