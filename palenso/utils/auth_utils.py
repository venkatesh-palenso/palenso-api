import uuid
import random
import string
import logging

from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from palenso.db.models import Token, User

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return "".join(random.choices(string.digits, k=length))


def generate_token():
    """Generate a unique token"""
    return uuid.uuid4().hex


def create_token(user, token_type, expires_in_hours=24):
    """Create a new token for the user"""
    token = Token.objects.create(
        user=user,
        token=generate_token(),
        token_type=token_type,
        expires_at=timezone.now() + timedelta(hours=expires_in_hours),
    )
    return token


def get_valid_token(token_value, token_type):
    """Get a valid token by value and type"""
    try:
        token = Token.objects.get(
            token=token_value, token_type=token_type, is_used=False
        )
        if not token.is_expired():
            return token
    except Token.DoesNotExist:
        pass
    return None


def mark_token_as_used(token):
    """Mark a token as used"""
    token.is_used = True
    token.used_at = timezone.now()
    token.save()


def send_email_verification(user, code):
    """Send email verification with OTP code using Twilio SendGrid"""
    try:
        subject = "Verify Your Email Address"
        message = f"""
        Hello {user.first_name or user.username},
        
        Your email verification code is: {code}
        
        This code will expire in 10 minutes.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        {settings.SITE_NAME}
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {user.email} using default backend")

    except Exception as e:
        logger.error(f"Failed to send email verification to {user.email}: {str(e)}")
        raise


def send_mobile_otp(user, otp):
    """Send OTP to mobile number using Twilio"""
    try:
        message = f"Your Palenso verification code is: {otp}. Valid for 10 minutes."

        # Use Twilio if configured, otherwise fallback to development mode
        if hasattr(settings, "TWILIO_ACCOUNT_SID") and settings.TWILIO_ACCOUNT_SID:
            from twilio.rest import Client
            from twilio.base.exceptions import TwilioException

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Send SMS via Twilio
            message_obj = client.messages.create(
                body=message, from_=settings.TWILIO_PHONE_NUMBER, to=user.mobile_number
            )

            logger.info(
                f"Twilio SMS sent to {user.mobile_number}, SID: {message_obj.sid}"
            )

        else:
            # Development mode - just log the OTP
            logger.info(f"Development mode - SMS to {user.mobile_number}: {message}")
            print(f"SMS to {user.mobile_number}: {message}")

    except Exception as e:
        logger.error(f"Failed to send SMS to {user.mobile_number}: {str(e)}")
        # In development, still print the OTP even if Twilio fails
        if settings.DEBUG:
            print(f"SMS to {user.mobile_number}: {message}")
        raise


def send_password_reset_email(user, token):
    """Send password reset email using Twilio SendGrid"""
    try:
        subject = "Reset Your Password"
        message = f"""
        Hello {user.first_name or user.username},
        
        You requested to reset your password. Click the link below to set a new password:
        
        {settings.SITE_URL}/reset-password/{token.token}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        {settings.SITE_NAME}
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email} using default backend")

    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        raise


def cleanup_expired_tokens():
    """Clean up expired tokens"""
    expired_tokens = Token.objects.filter(expires_at__lt=timezone.now())
    expired_tokens.delete()


def get_user_by_email_or_mobile(identifier):
    """Get user by email or mobile number"""
    try:
        if "@" in identifier:
            return User.objects.get(email=identifier.lower().strip())
        else:
            return User.objects.get(mobile_number=identifier.strip())
    except User.DoesNotExist:
        return None
