from rest_framework import serializers
from palenso.db.models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for education"""

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["company"]
