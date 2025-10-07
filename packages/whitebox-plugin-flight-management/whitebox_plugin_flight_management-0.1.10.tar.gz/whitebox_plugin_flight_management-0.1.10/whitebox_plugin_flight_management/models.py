from pathlib import Path

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from whitebox import settings
from whitebox.templatetags.whitebox import tagged_url


class TimestampBasedLifecycleQuerySet(models.QuerySet):
    def active(self):
        return self.filter(ended_at__isnull=True)

    def current(self):
        return self.active().first()

    async def acurrent(self):
        return await self.active().afirst()


class FlightSession(models.Model):
    name = models.CharField(max_length=128)

    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    objects = TimestampBasedLifecycleQuerySet.as_manager()

    @property
    def is_active(self):
        return self.ended_at is None


class FlightSessionRecordingStatus(models.IntegerChoices):
    NOT_READY = 10
    READY = 50


class FlightSessionRecording(models.Model):
    STATUSES = FlightSessionRecordingStatus

    flight_session = models.ForeignKey(
        FlightSession,
        on_delete=models.CASCADE,
        related_name="recordings",
    )
    provided_by_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
    )
    provided_by_id = models.IntegerField(null=True)
    provided_by = GenericForeignKey("provided_by_ct", "provided_by_id")

    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField()

    status = models.IntegerField(
        choices=FlightSessionRecordingStatus.choices,
        default=FlightSessionRecordingStatus.NOT_READY,
    )

    def get_provider(self):
        if not self.provided_by:
            return None

        return self.provided_by._meta.model_name

    def get_file_url(self):
        path = self.file.path

        if (
            path.startswith("http://")
            or path.startswith("https://")
            or path.startswith("ftp://")
        ):
            return path

        # In case of absolute paths, we first need to find it within the media
        # root folder
        if path.startswith("/"):
            path = Path(path).relative_to(settings.MEDIA_ROOT)

        return tagged_url(f"{settings.MEDIA_URL}{path}")


class KeyMoment(models.Model):
    flight_session = models.ForeignKey(
        FlightSession,
        on_delete=models.CASCADE,
        related_name="key_moments",
    )

    name = models.CharField(max_length=128)

    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    objects = TimestampBasedLifecycleQuerySet.as_manager()

    class Meta:
        ordering = ["started_at"]

    @property
    def is_active(self):
        return self.ended_at is None
