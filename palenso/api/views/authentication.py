# accounts.utils
import uuid
import re

# accounts.views

from django.utils import timezone

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from sentry_sdk import capture_exception, capture_message

from palenso.db.models import User
from palenso.api.serializers.people import UserInfoSerializer, UserSerializer
from palenso.utils.auth_utils import (
    create_token,
    generate_otp,
    get_valid_token,
    mark_token_as_used,
    send_email_verification,
    send_mobile_otp,
    send_password_reset_email,
)


PHONE_NUMBER_REGEX_PATTERN = ".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
EMAIL_ADDRESS_REGEX_PATTERN = (
    "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)


def check_valid_phone_number(phone_number):

    if len(phone_number) > 15:
        return False

    pattern = re.compile(PHONE_NUMBER_REGEX_PATTERN)
    return pattern.match(phone_number)


def check_valid_email_address(email_address):
    pattern = re.compile(EMAIL_ADDRESS_REGEX_PATTERN)
    return pattern.match(email_address)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return (
        str(refresh.access_token),
        str(refresh),
    )


class SignInEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email", False)
            mobile_number = request.data.get("mobile_number", False)
            password = request.data.get("password", False)

            if not email and not mobile_number:
                return Response(
                    {"error": "Please provide a valid email or mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and not check_valid_email_address(email):
                return Response(
                    {"error": "Please provide a valid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if mobile_number and not check_valid_phone_number(mobile_number):
                return Response(
                    {"error": "Please provide a valid mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email:
                user = User.objects.get(email=email)
            if mobile_number:
                user = User.objects.get(mobile_number=mobile_number)

            if not user.check_password(password):
                return Response(
                    {"error": "Invalid Credentials"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not user.is_active:
                return Response(
                    {
                        "error": "Your account has been deactivated. Please contact your site administrator."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            medium = "mobile_number" if mobile_number else "email"

            # settings last active for the user
            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_medium = medium
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.save()

            access_token, refresh_token = get_tokens_for_user(user)

            data = {"access_token": access_token, "refresh_token": refresh_token}

            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "Sorry, User not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# @ratelimit(key="ip", rate="5/h", block=True)
class SignUpEndpoint(APIView):

    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        try:
            first_name = request.data.get("first_name", "User")
            last_name = request.data.get("last_name", "")
            email = request.data.get("email", "")
            role = request.data.get("role", "student")

            channel = request.data.get("channel").strip().lower()

            if not channel:
                return Response(
                    {
                        "error": "Something went wrong. Please try again later or contact the support team."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate username
            username = uuid.uuid4().hex

            # Create user (inactive until password is set)
            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                is_active=False,  # User will be activated after password is set
            )
            user.save()

            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_medium = "email"
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.save()

            # Generate new verification code
            otp = generate_otp()
            token = create_token(
                user, "email_verification", expires_in_hours=1 / 6
            )  # 10 minutes
            token.token = otp
            token.save()
            send_email_verification(user, otp)

            serialized_user = UserInfoSerializer(user).data

            data = {
                "user": serialized_user,
                "message": "User created successfully. Please verify your contact information.",
            }

            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request):
        try:

            user_id = request.data.get("user_id")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            if password != confirm_password:
                return Response(
                    {"error": "passwords doesn't match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(pk=user_id)

            # Check if both email and mobile are verified
            if not user.is_email_verified:
                return Response(
                    {"error": "Email must be verified before completing signup."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user.mobile_number:
                if not user.is_mobile_verified:
                    return Response(
                        {
                            "error": "Mobile number must be verified before completing signup."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Set password and activate user
            user.set_password(password)
            user.is_active = True
            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_medium = "email"
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.save()

            access_token, refresh_token = get_tokens_for_user(user)

            data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "message": "Signup completed successfully.",
            }

            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "Sorry, User not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SignOutEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token", False)

            if not refresh_token:
                capture_message("No refresh token provided")
                return Response(
                    {
                        "error": "Something went wrong. Please try again later or contact the support team."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(pk=request.user.id)

            user.last_logout_time = timezone.now()
            user.last_logout_ip = request.META.get("REMOTE_ADDR")

            user.save()

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:

            email = request.data.get("email", False)
            mobile_number = request.data.get("mobile_number", False)

            if not email and not mobile_number:
                return Response(
                    {"error": "Please provide a valid email or mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and not check_valid_email_address(email):
                return Response(
                    {"error": "Please provide a valid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if mobile_number and not check_valid_phone_number(mobile_number):
                return Response(
                    {"error": "Please provide a valid mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email:
                user = User.objects.get(email=email)

            if mobile_number:
                user = User.objects.get(mobile_number=mobile_number)

            # Create password reset token
            token = create_token(user, "forgot_password", expires_in_hours=1)  # 1 hour
            send_password_reset_email(user, token)

            return Response(
                {"message": "Password reset email sent successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            token = request.data.get("token", False)
            new_password = request.data.get("new_password", False)
            confirm_password = request.data.get("confirm_password", False)
            if not token:
                return Response(
                    {"error": "token is missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if new_password != confirm_password:
                return Response(
                    {"error": "passwords doesn't match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = get_valid_token(token, "forgot_password")
            if not token:
                return Response(
                    {"error": "Invalid or expired reset token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = token.user
            user.set_password(new_password)
            user.save()

            mark_token_as_used(token)

            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user = User.objects.get(pk=request.user.id)

            old_password = request.data.get("old_password", False)
            new_password = request.data.get("new_password", False)
            confirm_password = request.data.get("confirm_password", False)

            if new_password != confirm_password:
                return Response(
                    {"error": "passwords doesn't match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if old_password == new_password or user.check_password(new_password):
                return Response(
                    {"error": "new password should be same as old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Sorry, User not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CheckMediumAvailabilityEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email", False)
            mobile_number = request.data.get("mobile_number", False)

            if not email and not mobile_number:
                return Response(
                    {"error": "Please provide a valid email or mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and not check_valid_email_address(email):
                return Response(
                    {"error": "Please provide a valid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if mobile_number and not check_valid_phone_number(mobile_number):
                return Response(
                    {"error": "Please provide a valid mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email:
                exists = User.objects.filter(email=email).exists()
                return Response(
                    {
                        "available": not exists,
                        "email": email,
                        "message": (
                            "Email is available."
                            if not exists
                            else "Email is already registered."
                        ),
                    },
                    status=status.HTTP_200_OK,
                )

            if mobile_number:
                exists = User.objects.filter(mobile_number=mobile_number).exists()
                return Response(
                    {
                        "available": not exists,
                        "mobile_number": mobile_number,
                        "message": (
                            "Mobile number is available."
                            if not exists
                            else "Mobile number is already registered."
                        ),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class RequestMediumVerificationEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email", False)
            mobile_number = request.data.get("mobile_number", False)
            user_id = request.data.get("user_id", False)

            if not email and not mobile_number:
                return Response(
                    {"error": "Please provide a valid email or mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and not check_valid_email_address(email):
                return Response(
                    {"error": "Please provide a valid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if mobile_number and not check_valid_phone_number(mobile_number):
                return Response(
                    {"error": "Please provide a valid mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and user_id:
                user = User.objects.get(pk=user_id)
                if user.is_email_verified:
                    return Response(
                        {"error": "Email is already verified."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user.is_email_verified = False
                user.email = email
                user.save()

                # Generate new verification code
                otp = generate_otp()
                token = create_token(
                    user, "email_verification", expires_in_hours=1 / 6
                )  # 10 minutes
                token.token = otp
                token.save()
                send_email_verification(user, otp)

                return Response(
                    {"message": "Verification email sent successfully."},
                    status=status.HTTP_200_OK,
                )

            if mobile_number and user_id:
                user = User.objects.get(pk=user_id)
                if user.is_mobile_verified:
                    return Response(
                        {"error": "Mobile number is already verified."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user.mobile_number = mobile_number
                user.is_mobile_verified = False
                user.save()

                # Generate new OTP
                otp = generate_otp()
                token = create_token(
                    user, "otp_verification", expires_in_hours=1 / 6
                )  # 10 minutes
                token.token = otp
                token.save()
                send_mobile_otp(user, otp)

                return Response(
                    {"message": "OTP sent successfully."},
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "Sorry, User not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            print("Request Verification", e)
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyMediumEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email", False)
            mobile_number = request.data.get("mobile_number", False)
            code = request.data.get("code", False)

            if not email and not mobile_number:
                return Response(
                    {"error": "Please provide a valid email or mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and not check_valid_email_address(email):
                return Response(
                    {"error": "Please provide a valid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if mobile_number and not check_valid_phone_number(mobile_number):
                return Response(
                    {"error": "Please provide a valid mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not code:
                return Response(
                    {"error": "Please provide a code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email:
                user = User.objects.get(email=email)
                token = get_valid_token(code, "email_verification")
                user.is_email_verified = True

            if mobile_number:
                user = User.objects.get(mobile_number=mobile_number)
                token = get_valid_token(code, "otp_verification")
                user.is_mobile_verified = True

            if not token or token.user != user:
                return Response(
                    {"error": "Invalid or expired verification code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.save()

            mark_token_as_used(token)

            return Response(
                {"message": "Verified successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CheckUserExistenceEndpoint(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email", False)
            mobile_number = request.data.get("mobile_number", False)

            if not email and not mobile_number:
                return Response(
                    {"error": "Please provide a valid email or mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email and not check_valid_email_address(email):
                return Response(
                    {"error": "Please provide a valid email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate mobile number if provided
            if mobile_number and not check_valid_phone_number(mobile_number):
                return Response(
                    {"error": "Please provide a valid mobile number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = None
            medium_used = None

            # Check by email first if provided
            if email:
                try:
                    user = User.objects.get(email=email)
                    medium_used = "email"
                except User.DoesNotExist:
                    pass

            # Check by mobile number if email not found or not provided
            if not user and mobile_number:
                try:
                    user = User.objects.get(mobile_number=mobile_number)
                    medium_used = "mobile_number"
                except User.DoesNotExist:
                    pass

            if user:
                # User exists
                response_data = {
                    "exists": True,
                    "medium_used": medium_used,
                    "has_password": True if user.password else False,
                    "is_active": user.is_active,
                    "is_email_verified": user.is_email_verified,
                    "is_mobile_verified": user.is_mobile_verified,
                    "role": user.role,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }

                # Add medium-specific verification status
                if medium_used == "email":
                    response_data["is_verified"] = user.is_email_verified
                elif medium_used == "mobile_number":
                    response_data["is_verified"] = user.is_mobile_verified

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # User doesn't exist
                response_data = {
                    "exists": False,
                    "medium_used": medium_used
                    or (email and "email")
                    or (mobile_number and "mobile_number"),
                }
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "error": "Something went wrong. Please try again later or contact the support team."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
