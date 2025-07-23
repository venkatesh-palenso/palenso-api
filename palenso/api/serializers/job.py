from rest_framework import serializers
from palenso.db.models import Job


class JobSerializer(serializers.ModelSerializer):
    """Serializer for education"""

    class Meta:
        model = Job
        fields = "__all__"
