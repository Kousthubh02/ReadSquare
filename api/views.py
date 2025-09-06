# views.py
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import login, logout
from django.utils import timezone

from .models import CustomUser
from .serializers import (
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    InitiateForgotPasswordSerializer,
    ResendEmailVerificationSerializer,
    ResetPasswordSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserRegistrationView(CreateAPIView):
    """
    API endpoint for user registration - creates user and sends email verification OTP
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully. Please check your email to verify your account.",
                "user": UserSerializer(user).data,
                "email_verification_required": True,
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    """
    API endpoint for regular user login using email and password
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        response_data = {
            "message": "Login successful",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }

        # Add warning if email is not verified
        if not user.is_verified:
            response_data["warning"] = "Please verify your email address"
            response_data["email_verification_required"] = True

        return Response(response_data, status=status.HTTP_200_OK)


class EmailVerificationView(APIView):
    """
    API endpoint to verify email using OTP
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "Email verified successfully", "user": UserSerializer(user).data}, status=status.HTTP_200_OK
        )


class ResendEmailVerificationView(CreateAPIView):
    """
    API endpoint to resend email verification OTP
    """

    serializer_class = ResendEmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {"message": result["message"], "email": result["email"], "expires_in_minutes": 10}, status=status.HTTP_200_OK
        )


class InitiateForgotPasswordView(CreateAPIView):
    """
    API endpoint to initiate forgot password - sends OTP to email
    """

    serializer_class = InitiateForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {"message": result["message"], "email": result["email"], "expires_in_minutes": 10}, status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    """
    API endpoint to reset password using OTP
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API endpoint for changing password when logged in
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update user profile
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Profile updated successfully", "user": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """
    Get current user profile
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def check_email_verification_status(request):
    """
    Check if current user's email is verified
    """
    user = request.user
    return Response(
        {
            "is_verified": user.is_verified,
            "email": user.email,
            "message": "Email is verified" if user.is_verified else "Email verification pending",
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_all_users(request):
    """
    Get all users (Admin only)
    """
    if not request.user.is_staff:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


class RefreshTokenView(APIView):
    """
    API endpoint to refresh JWT token
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            return Response({"access": str(token.access_token)})
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
