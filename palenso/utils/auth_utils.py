import uuid
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from palenso.db.models import Token, User


def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def generate_token():
    """Generate a unique token"""
    return uuid.uuid4().hex


def create_token(user, token_type, expires_in_hours=24):
    """Create a new token for the user"""
    token = Token.objects.create(
        user=user,
        token=generate_token(),
        token_type=token_type,
        expires_at=timezone.now() + timedelta(hours=expires_in_hours)
    )
    return token


def get_valid_token(token_value, token_type):
    """Get a valid token by value and type"""
    try:
        token = Token.objects.get(
            token=token_value,
            token_type=token_type,
            is_used=False
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
    """Send email verification with OTP code"""
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


def send_mobile_otp(user, otp):
    """Send OTP to mobile number"""
    # This is a placeholder. In production, you would integrate with an SMS service
    # like Twilio, AWS SNS, etc.
    message = f"Your verification code is: {otp}. Valid for 10 minutes."
    
    # For development, just print the OTP
    print(f"SMS to {user.mobile_number}: {message}")
    
    # In production, you would use something like:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=user.mobile_number
    # )


def send_password_reset_email(user, token):
    """Send password reset email"""
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


def cleanup_expired_tokens():
    """Clean up expired tokens"""
    expired_tokens = Token.objects.filter(expires_at__lt=timezone.now())
    expired_tokens.delete()


def get_user_by_email_or_mobile(identifier):
    """Get user by email or mobile number"""
    try:
        if '@' in identifier:
            return User.objects.get(email=identifier.lower().strip())
        else:
            return User.objects.get(mobile_number=identifier.strip())
    except User.DoesNotExist:
        return None 