from django.db import models

from palenso.db.models.base import BaseModel


class Company(BaseModel):
    """Company Profile for Employers"""

    COMPANY_SIZE_CHOICES = (
        ("1-10", "1-10 employees"),
        ("11-50", "11-50 employees"),
        ("51-200", "51-200 employees"),
        ("201-500", "201-500 employees"),
        ("501-1000", "501-1000 employees"),
        ("1000+", "1000+ employees"),
    )

    employer = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="company"
    )

    # Company Information
    name = models.CharField(max_length=200)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    company_size = models.CharField(
        max_length=20,
        choices=COMPANY_SIZE_CHOICES,
    )
    founded_year = models.DateField(null=True, blank=True)

    # Contact Information
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Location
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    # Company Media
    logo_url = models.URLField(
        blank=True, help_text="URL to company logo (AWS S3, etc.)"
    )
    banner_image_url = models.URLField(
        blank=True, help_text="URL to company banner (AWS S3, etc.)"
    )

    # Social Media
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)

    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
