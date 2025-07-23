from rest_framework.serializers import ModelSerializer, ReadOnlyField

from palenso.db.models.user import User
from palenso.db.models.profile import Profile


class UserSerializer(ModelSerializer):
    has_company = ReadOnlyField()

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class EmployerProfileSerializer(ModelSerializer):
    """Profile serializer for employees (excludes student-specific fields)"""

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "profile_picture_url",
            "bio",
            "date_of_birth",
            "gender",
            "linkedin",
            "github",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def to_representation(self, instance):
        """Custom representation to include profile picture URL"""
        data = super().to_representation(instance)
        # If profile_picture_url is empty, return None
        if not data.get("profile_picture_url"):
            data["profile_picture_url"] = None
        return data


class EmployerSerializer(ModelSerializer):
    """Complete employee serializer with user, profile, and company data"""

    profile = EmployerProfileSerializer(read_only=True)
    is_employer = ReadOnlyField()
    has_company = ReadOnlyField()
    is_employer_with_company = ReadOnlyField()

    class Meta:
        model = User
        fields = [
            # User basic info
            "id",
            "username",
            "email",
            "mobile_number",
            "first_name",
            "last_name",
            "role",
            # User status
            "is_active",
            "is_email_verified",
            "is_mobile_verified",
            "is_employer",
            "has_company",
            "is_employer_with_company",
            # User timestamps
            "date_joined",
            "last_active",
            "last_login_time",
            # Related data
            "profile",
            "company",
        ]
        read_only_fields = [
            "id",
            "username",
            "date_joined",
            "last_active",
            "last_login_time",
            "is_employer",
            "has_company",
            "is_employer_with_company",
        ]

    def to_representation(self, instance):
        """Custom representation to handle optional company data"""
        data = super().to_representation(instance)

        # Include company data only if it exists
        if hasattr(instance, "company") and instance.company:
            from palenso.api.serializers.company import CompanySerializer

            data["company"] = CompanySerializer(instance.company).data
        else:
            data["company"] = None

        return data
