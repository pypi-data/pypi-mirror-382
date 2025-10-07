from unittest.mock import patch, Mock
from django.test import TestCase

from whitebox_plugin_flight_management.serializers import KeyMomentSerializer
from whitebox_plugin_flight_management.handlers import (
    FlightStartHandler,
    FlightEndHandler,
    KeyMomentRecordHandler,
    KeyMomentFinishHandler,
    KeyMomentUpdateHandler,
    KeyMomentDeleteHandler,
)


class TestFlightStartHandler(TestCase):
    @patch(
        "whitebox_plugin_flight_management.services.FlightService.start_flight_session"
    )
    async def test_handle(self, mock_start_flight_session):
        sentinel = object()
        mock_start_flight_session.return_value = sentinel

        handler = FlightStartHandler()
        response = await handler.handle({})

        mock_start_flight_session.assert_awaited_once()
        self.assertEqual(
            response,
            {
                "flight_session": sentinel,
            },
        )


class TestFlightEndHandler(TestCase):
    @patch(
        "whitebox_plugin_flight_management.services.FlightService.end_flight_session"
    )
    async def test_handle(self, mock_end_flight_session):
        sentinel = object()
        mock_end_flight_session.return_value = sentinel

        handler = FlightEndHandler()
        response = await handler.handle({})

        mock_end_flight_session.assert_awaited_once()
        self.assertEqual(
            response,
            {
                "flight_session": sentinel,
            },
        )


class TestKeyMomentRecordHandler(TestCase):
    @patch("whitebox_plugin_flight_management.services.FlightService.record_key_moment")
    async def test_handle(self, mock_record_key_moment):
        sentinel = object()
        mock_record_key_moment.return_value = sentinel

        handler = KeyMomentRecordHandler()
        response = await handler.handle({})

        mock_record_key_moment.assert_awaited_once()
        self.assertEqual(
            response,
            {
                "key_moment": sentinel,
            },
        )


class TestKeyMomentFinishHandler(TestCase):
    @patch("whitebox_plugin_flight_management.services.FlightService.finish_key_moment")
    async def test_handle(self, mock_finish_key_moment):
        sentinel = object()
        mock_finish_key_moment.return_value = sentinel

        handler = KeyMomentFinishHandler()
        response = await handler.handle({})

        mock_finish_key_moment.assert_awaited_once()
        self.assertEqual(
            response,
            {
                "key_moment": sentinel,
            },
        )


class TestKeyMomentUpdateHandler(TestCase):
    @patch("whitebox_plugin_flight_management.services.FlightService.update_key_moment")
    async def test_handle(self, mock_update_key_moment):
        sentinel = object()
        mock_update_key_moment.return_value = sentinel

        handler = KeyMomentUpdateHandler()
        response = await handler.handle({"key_moment_id": 1, "name": "Updated"})

        mock_update_key_moment.assert_awaited_once_with(key_moment_id=1, name="Updated")
        self.assertEqual(
            response,
            {
                "key_moment": sentinel,
            },
        )


class TestKeyMomentDeleteHandler(TestCase):
    @patch("whitebox_plugin_flight_management.services.FlightService.delete_key_moment")
    async def test_handle(self, mock_delete_key_moment):
        flight_session_id = 123
        key_moment_id = 456

        mock_key_moment = Mock(flight_session_id=flight_session_id)
        mock_delete_key_moment.return_value = mock_key_moment

        handler = KeyMomentDeleteHandler()
        response = await handler.handle({"key_moment_id": key_moment_id})

        mock_delete_key_moment.assert_awaited_once_with(
            key_moment_id=key_moment_id,
        )
        self.assertEqual(
            response,
            {
                "flight_session_id": mock_key_moment.flight_session_id,
                "key_moment_id": key_moment_id,
            },
        )
