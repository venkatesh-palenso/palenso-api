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

from palenso.db.models import User, Token, Profile
from palenso.api.serializers.auth import (
    UserSerializer, CheckAvailabilitySerializer, CreateUserSerializer, SendVerificationCodeSerializer,
    CompleteSignupSerializer, SignInSerializer, VerifyEmailSerializer,
    VerifyMobileSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from palenso.utils.auth_utils import (
    generate_otp, create_token, get_valid_token, mark_token_as_used,
    send_email_verification, send_mobile_otp, send_password_reset_email,
    get_user_by_email_or_mobile
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
            serializer = SignInSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            email = data.get('email')
            mobile_number = data.get('mobile_number')
            password = data.get('password')
            
            # Determine medium and get user
            if email:
                medium = "email"
                try:
                    user = User.objects.get(email=email.lower().strip())
                except User.DoesNotExist:
                    return Response(
                        {"error": "Invalid credentials."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif mobile_number:
                medium = "mobile"
                try:
                    user = User.objects.get(mobile_number=mobile_number.strip())
                except User.DoesNotExist:
                    return Response(
                        {"error": "Invalid credentials."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": "Either email or mobile number is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not user.check_password(password):
                return Response(
                    {"error": "Invalid credentials."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            if not user.is_active:
                return Response(
                    {"error": "Your account has been deactivated. Please contact your site administrator."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serialized_user = UserSerializer(user).data

            # Update user activity
            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_medium = medium
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.save()

            access_token, refresh_token = get_tokens_for_user(user)

            data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": serialized_user,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CheckAvailabilityEndpoint(APIView):
    """Check if email or mobile number is available for registration"""
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            serializer = CheckAvailabilitySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data.get('email')
            mobile_number = serializer.validated_data.get('mobile_number')
            
            if email:
                email = email.lower().strip()
                exists = User.objects.filter(email=email).exists()
                return Response({
                    "available": not exists,
                    "email": email,
                    "message": "Email is available." if not exists else "Email is already registered."
                }, status=status.HTTP_200_OK)
            
            elif mobile_number:
                mobile_number = mobile_number.strip()
                exists = User.objects.filter(mobile_number=mobile_number).exists()
                return Response({
                    "available": not exists,
                    "mobile_number": mobile_number,
                    "message": "Mobile number is available." if not exists else "Mobile number is already registered."
                }, status=status.HTTP_200_OK)

        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserSignupEndpoint(APIView):
    """Create user with contact information (supports SSO flow)"""
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            serializer = CreateUserSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            first_name = data.get('first_name')
            last_name = data.get('last_name', '')
            email = data.get('email')
            role = data.get('role', 'student')
            

            # Normalize data
            if email:
                email = email.lower().strip()
            

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

            # Generate new verification code
            otp = generate_otp()
            token = create_token(user, 'email_verification', expires_in_hours=1/6)  # 10 minutes
            token.token = otp
            token.save()
            send_email_verification(user, otp)

            # Create profile
            Profile.objects.create(user=user)

            serialized_user = UserSerializer(user).data
            
            data = {
                "user": serialized_user,
                "message": "User created successfully. Please verify your contact information.",
            }

            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request):
        try:
            serializer = CompleteSignupSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = serializer.validated_data['user_id']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(id=user_id, is_active=False)
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid user ID or user not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Check if both email and mobile are verified
            if not user.is_email_verified:
                return Response(
                    {"error": "Email must be verified before completing signup."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if user.mobile_number:
                if not user.is_mobile_verified:
                    return Response(
                        {"error": "Mobile number must be verified before completing signup."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            
            # Set password and activate user
            user.set_password(password)
            user.is_active = True
            user.last_active = timezone.now()
            user.last_login_time = timezone.now()
            user.last_login_ip = request.META.get("REMOTE_ADDR")
            user.last_login_medium = "email" if user.email else "mobile"
            user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
            user.token_updated_at = timezone.now()
            user.save()

            serialized_user = UserSerializer(user).data
            access_token, refresh_token = get_tokens_for_user(user)
            
            data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": serialized_user,
                "message": "Signup completed successfully.",
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class SendVerificationCodeEndpoint(APIView):
    """Send verification codes for email or mobile"""
    permission_classes = (AllowAny,)
    
    def post(self, request):
        try:
            serializer = SendVerificationCodeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data.get('email')
            mobile_number = serializer.validated_data.get('mobile_number')
            user_id = serializer.validated_data.get('user_id')
            
            # Get user by email or mobile
            if email:
                try:
                    user = User.objects.get(email=email.lower().strip())
                except User.DoesNotExist:
                    return Response(
                        {"error": "User not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                if user.is_email_verified:
                    return Response(
                        {"error": "Email is already verified."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                # Generate new verification code
                otp = generate_otp()
                token = create_token(user, 'email_verification', expires_in_hours=1/6)  # 10 minutes
                token.token = otp
                token.save()
                send_email_verification(user, otp)
                
                return Response(
                    {"message": "Verification email sent successfully."},
                    status=status.HTTP_200_OK,
                )
            
            elif user_id and mobile_number:
                try:
                    user = User.objects.get(id=int(user_id))
                except User.DoesNotExist:
                    return Response(
                        {"error": "User not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                if user.is_mobile_verified:
                    return Response(
                        {"error": "Mobile number is already verified."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                # Generate new OTP
                otp = generate_otp()
                token = create_token(user, 'otp_verification', expires_in_hours=1/6)  # 10 minutes
                token.token = otp
                token.save()
                send_mobile_otp(user, otp)

                user.mobile_number = mobile_number
                user.save()
                
                return Response(
                    {"message": "OTP sent successfully."},
                    status=status.HTTP_200_OK,
                )
            
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
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
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.get(pk=request.user.id)
            user.last_logout_time = timezone.now()
            user.last_logout_ip = request.META.get("REMOTE_ADDR")
            user.save()

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully signed out"}, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyEmailEndpoint(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = VerifyEmailSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                user = User.objects.get(email=email.lower().strip())
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            token = get_valid_token(code, 'email_verification')
            if not token or token.user != user:
                return Response(
                    {"error": "Invalid or expired verification code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            user.is_email_verified = True
            user.save()
            
            mark_token_as_used(token)
            
            return Response(
                {"message": "Email verified successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyMobileEndpoint(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = VerifyMobileSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            mobile_number = serializer.validated_data['mobile_number']
            otp = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            token = get_valid_token(otp, 'otp_verification')
            if not token or token.user != user:
                return Response(
                    {"error": "Invalid or expired OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            user.is_mobile_verified = True
            user.save()
            
            mark_token_as_used(token)
            
            return Response(
                {"message": "Mobile number verified successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )





class ForgotPasswordEndpoint(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email.lower().strip())
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Create password reset token
            token = create_token(user, 'forgot_password', expires_in_hours=1)  # 1 hour
            send_password_reset_email(user, token)
            
            return Response(
                {"message": "Password reset email sent successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordEndpoint(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            token_value = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            token = get_valid_token(token_value, 'forgot_password')
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
                {"error": "Something went wrong. Please try again later or contact the support team."},
                status=status.HTTP_400_BAD_REQUEST,
            )
