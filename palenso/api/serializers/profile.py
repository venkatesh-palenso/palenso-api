from rest_framework import serializers

from palenso.api.serializers.people import UserSerializer
from palenso.db.models.profile import (
    Education,
    Interest,
    Profile,
    Project,
    Resume,
    Skill,
    WorkExperience,
)
from palenso.db.models.user import User


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user"]

    def to_representation(self, instance):
        """Custom representation to include profile picture URL"""
        data = super().to_representation(instance)
        # If profile_picture_url is empty, return None
        if not data.get("profile_picture_url"):
            data["profile_picture_url"] = None
        return data


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education"""

    class Meta:
        model = Education
        fields = "__all__"


class WorkExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience"""

    class Meta:
        model = WorkExperience
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills"""

    class Meta:
        model = Skill
        fields = "__all__"


class InterestSerializer(serializers.ModelSerializer):
    """Serializer for interests"""

    class Meta:
        model = Interest
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects"""

    class Meta:
        model = Project
        fields = "__all__"


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for resumes"""

    class Meta:
        model = Resume
        fields = "__all__"

    def to_representation(self, instance):
        """Custom representation to include file URL"""
        data = super().to_representation(instance)
        # If file_url is empty, return None
        if not data.get("file_url"):
            data["file_url"] = None
        return data


class StudentProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer with all related data"""

    profile = ProfileSerializer(read_only=True)

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
        ]
        read_only_fields = ["id", "username", "date_joined", "last_active"]

    def to_representation(self, instance):
        """Custom representation to include related data"""
        data = super().to_representation(instance)
        if hasattr(instance, "profile") and instance.profile:
            data["education"] = EducationSerializer(
                instance.profile.education.all(), many=True
            ).data
            data["work_experience"] = WorkExperienceSerializer(
                instance.profile.work_experience.all(), many=True
            ).data
            data["skills"] = SkillSerializer(
                instance.profile.skills.all(), many=True
            ).data
            data["interests"] = InterestSerializer(
                instance.profile.interests.all(), many=True
            ).data
            data["projects"] = ProjectSerializer(
                instance.profile.projects.all(), many=True
            ).data
            data["resumes"] = ResumeSerializer(
                instance.profile.resumes.all(), many=True
            ).data
        return data
