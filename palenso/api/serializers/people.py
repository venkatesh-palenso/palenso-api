from rest_framework.serializers import ModelSerializer, ReadOnlyField

from palenso.db.models.user import User


class UserSerializer(ModelSerializer):
    is_employer = ReadOnlyField()
    has_company = ReadOnlyField()
    is_employer_with_company = ReadOnlyField()
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }