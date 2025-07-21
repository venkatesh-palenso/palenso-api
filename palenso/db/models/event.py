from django.db import models

from palenso.db.models.base import BaseModel
from palenso.db.models.company import Company


class Event(BaseModel):
    """Event Model for Employers"""

    organizer = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="organized_events"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="events", null=True, blank=True
    )

    # Event Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(
        max_length=20,
        choices=[
            ("workshop", "Workshop"),
            ("seminar", "Seminar"),
            ("conference", "Conference"),
            ("hackathon", "Hackathon"),
            ("career_fair", "Career Fair"),
            ("networking", "Networking Event"),
            ("webinar", "Webinar"),
            ("other", "Other"),
        ],
    )

    # Date and Time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)

    # Location
    location = models.CharField(max_length=200)
    is_virtual = models.BooleanField(default=False)
    virtual_meeting_url = models.URLField(blank=True)

    # Capacity and Registration
    max_participants = models.IntegerField(null=True, blank=True)
    is_registration_required = models.BooleanField(default=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Event Media
    banner_image_url = models.URLField(
        blank=True, help_text="URL to event banner (AWS S3, etc.)"
    )

    # Additional Information
    tags = models.TextField(blank=True)  # Comma-separated tags
    requirements = models.TextField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = "events"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    @property
    def registration_count(self):
        return self.registrations.count()

    @property
    def is_registration_open(self):
        if self.registration_deadline:
            from django.utils import timezone

            return timezone.now() < self.registration_deadline
        return True

    @property
    def is_full(self):
        if self.max_participants:
            return self.registration_count >= self.max_participants
        return False


class EventRegistration(BaseModel):
    """Event Registration Model"""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    participant = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="event_registrations"
    )

    # Registration Details
    registration_date = models.DateTimeField(auto_now_add=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("registered", "Registered"),
            ("confirmed", "Confirmed"),
            ("attended", "Attended"),
            ("cancelled", "Cancelled"),
            ("no_show", "No Show"),
        ],
        default="registered",
    )

    # Additional Information
    dietary_restrictions = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Payment Information (if applicable)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("refunded", "Refunded"),
        ],
        default="pending",
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "event_registrations"
        ordering = ["-registration_date"]
        unique_together = ["event", "participant"]

    def __str__(self):
        return f"{self.participant.get_full_name()} - {self.event.title}"
