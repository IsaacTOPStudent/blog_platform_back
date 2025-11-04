
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import User
from .serializers import RegisterSerializer, EmailAuthTokenSerializer, UserSerializer

class LoginView(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer

    @extend_schema(
        operation_id="user_login",
        description="Authenticate user with email and password, returning an auth token.",
        request=EmailAuthTokenSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful",
                examples=[
                    OpenApiExample(
                        "LoginSuccess",
                        value={"token": "2e32c3f24b3047a39fba6d70fdc03d22d1b7c3f9"}
                    )
                ]
            ),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        tags=["users"],
    )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data

        return Response({
            'token': token.key,
            'user': user_data
        })


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    @extend_schema(
        operation_id="user_register",
        description="Register a new user. A default team will be assigned if none is provided.",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User created successfully",
                examples=[
                    OpenApiExample(
                        "RegisterSuccess",
                        value={
                            "id": 1,
                            "username": "newuser",
                            "email": "newuser@example.com"
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation error (email already exists, weak password, etc.)"),
        },
        tags=["users"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogOutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="user_logout",
        description="Invalidate the current user's authentication token.",
        responses={
            200: OpenApiResponse(
                description="Logout successful",
                examples=[OpenApiExample("LogoutSuccess", value={"message": "Logout successful"})]
            ),
            400: OpenApiResponse(description="User is not logged in"),
            401: OpenApiResponse(description="Not authenticated"),
        },
        tags=["users"],
    )

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "User is not logged in"}, status=status.HTTP_400_BAD_REQUEST)
    



