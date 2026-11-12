
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles_app.models import Profile

from .serializers import LoginSerializer, RegistrationSerializer


class LoginView(APIView):
    """API view for logging in users."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Log in a user and return their auth token.

        Args:
            request (Request): The HTTP request with ``username`` and
                ``password`` in its body.

        Returns:
            Response: The token, username, email and user ID with status
                200, or the validation errors with status 400.
        """
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )


class RegistrationView(APIView):
    """API view for registering new users."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user and create their profile and auth token.

        Args:
            request (Request): The HTTP request with ``username``,
                ``email``, ``password``, ``repeated_password`` and ``type``
                in its body.

        Returns:
            Response: The token, username, email and user ID with status
                201, or the validation errors with status 400.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            with transaction.atomic():
                saved_account = serializer.save()

                Profile.objects.create(user=saved_account)

                token, created = Token.objects.get_or_create(
                    user=saved_account
                )

            data = {
                "token": token.key,
                "username": saved_account.username,
                "email": saved_account.email,
                "user_id": saved_account.id,
            }

            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
