from urllib.parse import urljoin
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator

from palenso.db.models.base import BaseModel


class MediaAssets(BaseModel):
    """Model to store media files with URL support"""

    ASSET_TYPES = (
        ("profile_picture", "Profile Picture"),
        ("resume", "Resume"),
        ("project_image", "Project Image"),
        ("company_logo", "Company Logo"),
        ("company_banner", "Company Banner"),
        ("event_banner", "Event Banner"),
        ("other", "Other"),
    )

    file = models.FileField(
        upload_to="media_assets/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]
            )
        ],
    )

    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "media_assets"
        verbose_name_plural = "Media Assets"

    def __str__(self):
        return f"{self.asset_type} - {self.created_by.username}"

    @property
    def display_url(self):
        """Return the full URL to the file"""
        # S3 or external URL is returned directly by file.url
        file_url = self.file.url

        # For local development: prepend host if not already absolute
        if settings.DEBUG and not file_url.startswith("http"):
            host = getattr(settings, "HOST_URL", "http://localhost:8000")  # fallback
            return urljoin(host, file_url)

        return file_url
