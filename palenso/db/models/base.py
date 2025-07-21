import uuid
from django.db import models

from crum import get_current_user

from ..mixins import AuditModel


class BaseModel(AuditModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user and not user.is_anonymous:
            if not self.pk and not self.created_by:
                self.created_by = user
            self.updated_by = user

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.uuid)
