import logging

from django.db.models.query import Prefetch
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from .models import (
    FlightSession,
    KeyMoment,
)
from .serializers import (
    FlightSessionSerializer,
)


logger = logging.getLogger(__name__)


class FlightSessionViewSet(GenericViewSet, ListModelMixin):
    # Sort flight sessions in timestamp-descending order, and key moments in
    # timestamp-ascending order for easier readability
    queryset = FlightSession.objects.prefetch_related(
        "recordings", "key_moments"
    ).order_by("-started_at")
    serializer_class = FlightSessionSerializer
