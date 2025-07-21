from rest_framework import serializers
from palenso.api.serializers.profile import ProfileSerializer
from palenso.db.models import Company
from palenso.db.models.user import User


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for education"""

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["company"]


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer with all related data"""

    profile = ProfileSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "mobile_number",
            "first_name",
            "last_name",
            "is_email_verified",
            "is_mobile_verified",
            "is_active",
            "date_joined",
            "last_active",
            "profile",
            "company",
        ]
        read_only_fields = ["id", "username", "date_joined", "last_active"]
