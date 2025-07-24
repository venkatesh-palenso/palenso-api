from rest_framework import serializers

from palenso.api.serializers.people import UserInfoSerializer
from palenso.api.serializers.company import CompanySerializer

from palenso.db.models import (
    Profile,
    Education,
    WorkExperience,
    Skill,
    Project,
    Interest,
    Resume,
)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for profile"""

    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["id", "user"]


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


class UserProfileSerializer(serializers.Serializer):
    """Serializer that combines User and Profile data into one flat structure"""

    def to_representation(self, instance):
        user_data = UserInfoSerializer(instance).data
        profile_data = ProfileSerializer(instance.profile).data

        return {
            "user_id": instance.id,
            "profile_id": instance.profile.id,
            **user_data,
            **profile_data,
        }


class StudentProfileSerializer(serializers.Serializer):
    """Final serializer with flat user/profile fields and grouped relations"""

    educations = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    resumes = serializers.SerializerMethodField()

    def to_representation(self, instance):
        user_data = UserProfileSerializer(instance).data
        profile = instance.profile

        return {
            **user_data,
            "educations": self.get_educations(profile),
            "projects": self.get_projects(profile),
            "experiences": self.get_experiences(profile),
            "skills": self.get_skills(profile),
            "interests": self.get_interests(profile),
            "resumes": self.get_resumes(profile),
        }

    def get_educations(self, profile):
        return EducationSerializer(profile.educations.all(), many=True).data

    def get_projects(self, profile):
        return ProjectSerializer(profile.projects.all(), many=True).data

    def get_experiences(self, profile):
        return WorkExperienceSerializer(profile.work_experiences.all(), many=True).data

    def get_skills(self, profile):
        return SkillSerializer(profile.skills.all(), many=True).data

    def get_interests(self, profile):
        return InterestSerializer(profile.interests.all(), many=True).data

    def get_resumes(self, profile):
        return ResumeSerializer(profile.resumes.all(), many=True).data


class EmployerProfileSerializer(serializers.Serializer):
    """Serializer for employer profile"""

    def to_representation(self, instance):
        # instance is a User
        user_data = UserProfileSerializer(instance).data
        company_data = (
            CompanySerializer(instance.company).data
            if hasattr(instance, "company")
            else None
        )

        return {
            **user_data,  # flattened user + profile data
            "company": company_data,  # nested company data
        }
