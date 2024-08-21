from notion.models.enum.priority_enum import PriorityEnum
from notion.models.enum.status_enum import StatusEnum
from django.db import models
import uuid


class Notion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=StatusEnum.choices)
    priority = models.CharField(max_length=20, choices=PriorityEnum.choices)

    class Meta:
        verbose_name = "Notion"
        verbose_name_plural = "Notions"
