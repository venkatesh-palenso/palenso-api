from rest_framework import serializers
from palenso.db.models.event import Event, EventRegistration
from palenso.api.serializers.company import CompanySerializer


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    company = CompanySerializer(read_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    organizer_name = serializers.CharField(source="organizer.get_full_name", read_only=True)
    registration_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id", "organizer", "organizer_name", "company", "company_id", "title",
            "description", "event_type", "start_date", "end_date", "registration_deadline",
            "location", "is_virtual", "virtual_meeting_url", "max_participants",
            "is_registration_required", "registration_fee", "banner_image_url",
            "tags", "requirements", "is_active", "is_featured", "registration_count",
            "is_registration_open", "is_full", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "organizer", "created_at", "updated_at", "registration_count",
            "is_registration_open", "is_full"
        ]


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for EventRegistration model"""
    event = EventSerializer(read_only=True)
    event_id = serializers.IntegerField(write_only=True)
    participant_name = serializers.CharField(source="participant.get_full_name", read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            "id", "event", "event_id", "participant", "participant_name",
            "registration_date", "status", "dietary_restrictions", "special_requirements",
            "notes", "payment_status", "payment_amount", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "participant", "registration_date", "created_at", "updated_at"]
