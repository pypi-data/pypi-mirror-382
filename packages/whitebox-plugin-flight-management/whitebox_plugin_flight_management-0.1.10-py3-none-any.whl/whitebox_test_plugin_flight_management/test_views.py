from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from whitebox_plugin_flight_management.models import FlightSession, KeyMoment
from whitebox_plugin_flight_management.serializers import FlightSessionSerializer


class TestFlightSessionViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("whitebox_plugin_flight_management:flight-session-list")

        # Create some flight sessions and key moments
        self.flight_session1 = FlightSession.objects.create(name="Session 1")
        self.flight_session2 = FlightSession.objects.create(name="Session 2")

        KeyMoment.objects.create(
            flight_session=self.flight_session1,
            name="Key Moment 1",
        )
        KeyMoment.objects.create(
            flight_session=self.flight_session2,
            name="Key Moment 2",
        )

    def test_list_flight_sessions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data matches the serialized flight sessions
        flight_sessions = FlightSession.objects.order_by("-started_at")
        serializer = FlightSessionSerializer(flight_sessions, many=True)
        self.assertEqual(response.data, serializer.data)
