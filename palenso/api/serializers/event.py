from rest_framework import serializers
from palenso.db.models.event import Event, EventRegistration
from palenso.db.models.user import User
from palenso.api.serializers.company import CompanySerializer
import uuid


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    company = CompanySerializer(read_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    organizer_name = serializers.CharField(source="organizer.get_full_name", read_only=True)
    organizer_email = serializers.CharField(source="organizer.email", read_only=True)
    organizer_phone = serializers.CharField(source="organizer.mobile_number", read_only=True)
    registration_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id", "organizer", "organizer_name", "organizer_email", "organizer_phone", "company", "company_id", "title",
            "description", "event_type", "start_date", "end_date", "registration_deadline",
            "location", "is_virtual", "virtual_meeting_url", "max_participants",
            "is_registration_required", "registration_fee", "banner_image_url",
            "tags", "requirements", "is_active", "is_featured", "registration_count",
            "is_registration_open", "is_full", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "organizer", "organizer_email", "organizer_phone", "created_at", "updated_at", "registration_count",
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


class AnonymousEventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for Anonymous Event Registration that creates dummy users"""
    
    # Anonymous user fields
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    mobile_number = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    # Event registration fields
    event_id = serializers.UUIDField(write_only=True, required=True)
    dietary_restrictions = serializers.CharField(required=False, allow_blank=True)
    special_requirements = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = EventRegistration
        fields = [
            "first_name", "last_name", "email", "mobile_number",
            "event_id", "dietary_restrictions", "special_requirements", "notes"
        ]
    
    def validate_event_id(self, value):
        """Validate that the event exists and registration is open"""
        try:
            event = Event.objects.get(pk=value)
            if not event.is_active:
                raise serializers.ValidationError("This event is not active.")
            if not event.is_registration_open:
                raise serializers.ValidationError("Registration for this event is closed.")
            if event.is_full:
                raise serializers.ValidationError("This event is full.")
            return value
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
    
    def validate_email(self, value):
        """Check if email is already registered for this event"""
        event_id = self.initial_data.get('event_id')
        if event_id:
            try:
                event = Event.objects.get(pk=event_id)
                if EventRegistration.objects.filter(
                    event=event, 
                    participant__email=value.lower()
                ).exists():
                    raise serializers.ValidationError("You are already registered for this event with this email.")
            except Event.DoesNotExist:
                pass
        return value.lower()
    
    def create(self, validated_data):
        """Create a dummy user and event registration"""
        # Extract user data
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        mobile_number = validated_data.pop('mobile_number', '')
        
        # Extract event registration data
        event_id = validated_data.pop('event_id')
        dietary_restrictions = validated_data.pop('dietary_restrictions', '')
        special_requirements = validated_data.pop('special_requirements', '')
        notes = validated_data.pop('notes', '')
        
        # Check if user with this email already exists
        try:
            user = User.objects.get(email=email)
            # If user exists but is not a dummy user, we might want to handle this differently
            if not user.is_dummy_user:
                # For now, we'll create a new dummy user with a different username
                user = User.create_dummy_user(first_name, last_name, email, mobile_number)
        except User.DoesNotExist:
            # Create new dummy user
            user = User.create_dummy_user(first_name, last_name, email, mobile_number)
        
        # Get the event
        event = Event.objects.get(pk=event_id)
        
        # Create event registration
        registration = EventRegistration.objects.create(
            event=event,
            participant=user,
            dietary_restrictions=dietary_restrictions,
            special_requirements=special_requirements,
            notes=notes,
            status='registered',
            payment_status='pending',
            payment_amount=event.registration_fee,
        )
        
        return registration
