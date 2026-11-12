from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Account created successfully.",
            "token": token.key,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        }, status=status.HTTP_201_CREATED)


class AuthRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "message": "Biz authentication API",
            "endpoints": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "logout": "/api/auth/logout/",
                "me": "/api/auth/me/",
            },
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        password = request.data.get("password", "")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful.",
            "token": token.key,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response({"message": "Logged out successfully."})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
