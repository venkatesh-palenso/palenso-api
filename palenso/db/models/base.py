import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator

from crum import get_current_user

from ..mixins import AuditModel


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username=username)


class Token(models.Model):
    """Model to store different types of tokens"""
    TOKEN_TYPES = (
        ('bearer', 'Bearer Token'),
        ('email_verification', 'Email Verification'),
        ('otp_verification', 'OTP Verification'),
        ('forgot_password', 'Forgot Password'),
    )
    
    id = models.BigAutoField(unique=True, primary_key=True)
    token = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tokens')
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'auth_tokens'
        indexes = [
            models.Index(fields=['token', 'token_type']),
            models.Index(fields=['user', 'token_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.token_type}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class User(AbstractBaseUser):
    id = models.BigAutoField(unique=True, primary_key=True)

    username = models.CharField(max_length=128, unique=True)
    
    objects = UserManager()

    # user fields
    mobile_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    email = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    
    # choices for role student, employer
    role = models.CharField(max_length=255, blank=True, choices=[('student', 'Student'), ('employer', 'Employer')], default='student')

    # tracking metrics
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_location = models.CharField(max_length=255, blank=True)
    created_location = models.CharField(max_length=255, blank=True)

    # the is' es
    is_superuser = models.BooleanField(default=False)
    is_managed = models.BooleanField(default=False)
    is_password_expired = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    is_password_autoset = models.BooleanField(default=False)

    token = models.CharField(max_length=64, blank=True)

    billing_address_country = models.CharField(max_length=255, default="INDIA")
    billing_address = models.JSONField(null=True)
    has_billing_address = models.BooleanField(default=False)

    user_timezone = models.CharField(max_length=255, default="Asia/Kolkata")

    last_active = models.DateTimeField(default=timezone.now, null=True)
    last_login_time = models.DateTimeField(null=True)
    last_logout_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(
        max_length=20,
        default="email",
    )
    last_login_uagent = models.TextField(blank=True)
    token_updated_at = models.DateTimeField(null=True)

    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower().strip()
        if self.mobile_number:
            self.mobile_number = self.mobile_number.strip()

        if self.token_updated_at is not None:
            self.token = uuid.uuid4().hex + uuid.uuid4().hex
            self.token_updated_at = timezone.now()

        if self.is_superuser:
            self.is_staff = True

        super(User, self).save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    def has_perm(self, perm, obj=None):
        """Return True if the user has the specified permission."""
        if self.is_active and self.is_superuser:
            return True
        return False
    
    def has_module_perms(self, app_label):
        """Return True if the user has permission to access the given app."""
        if self.is_active and self.is_superuser:
            return True
        return False
    
    def has_perms(self, perm_list, obj=None):
        """Return True if the user has each of the specified permissions."""
        return all(self.has_perm(perm, obj) for perm in perm_list)


class BaseModel(AuditModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user is None or user.is_anonymous:
            self.created_by = None
            self.updated_by = None
            super(BaseModel, self).save(*args, **kwargs)
        else:
            self.created_by = user
            self.updated_by = user
            super(BaseModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.uuid)

