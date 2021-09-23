from django.db import models
import uuid


class AbstractUUIDModel(models.Model):
    pkid = models.\
            BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True
