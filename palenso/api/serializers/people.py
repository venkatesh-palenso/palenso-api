from rest_framework.serializers import ModelSerializer

from palenso.db.models import User


class UserSerializer(ModelSerializer):
    """Serializer for user"""

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class UserInfoSerializer(ModelSerializer):
    """Serializer for authenticated user"""

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "role",
            "is_email_verified",
            "is_mobile_verified",
            "is_active",
            "date_joined",
            "is_password_expired",
            "last_login_time"
        ]
