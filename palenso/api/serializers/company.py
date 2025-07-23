from rest_framework import serializers
from palenso.db.models.company import Company


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    employer_name = serializers.CharField(source="employer.get_full_name", read_only=True)

    class Meta:
        model = Company
        fields = [
            "id", "employer", "employer_name", "name", "description", "industry",
            "company_size", "founded_year", "website", "email", "phone", "country",
            "state", "city", "address", "logo_url", "banner_image_url", "linkedin",
            "twitter", "facebook", "is_verified", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "employer", "created_at", "updated_at"]
