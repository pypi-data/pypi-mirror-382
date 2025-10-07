from contextlib import nullcontext
from unittest.mock import patch
from django.test.testcases import TransactionTestCase

from whitebox_plugin_flight_management.models import FlightSession, KeyMoment
from whitebox_plugin_flight_management.services import FlightService


@patch(
    "whitebox_plugin_flight_management.services.FlightService._lock",
    nullcontext,
)
class TestFlightService(TransactionTestCase):
    async def test_get_current_flight_session(self):
        # GIVEN no flight session is active
        initial = await FlightService.get_current_flight_session()
        self.assertIsNone(initial)

        # WHEN a flight session is started
        created = await FlightService.start_flight_session()

        # THEN the current flight session should be the one that was created
        current = await FlightService.get_current_flight_session()
        self.assertEqual(current.pk, created.pk)

    async def test_get_flight_session_by_id(self):
        # GIVEN a flight session is created
        created = await FlightSession.objects.acreate()

        # WHEN retrieving the flight session by ID
        session = await FlightService.get_flight_session_by_id(created.pk)

        # THEN the retrieved session should match the created one
        self.assertEqual(session.pk, created.pk)

    async def test_record_key_moment(self):
        # GIVEN a flight session is started
        await FlightService.start_flight_session()

        # WHEN recording a key moment
        key_moment = await FlightService.record_key_moment()

        # THEN a key moment should be recorded
        self.assertIsNotNone(key_moment)
        self.assertEqual(key_moment.name, "Key Moment #1")

    async def test_finish_key_moment(self):
        # GIVEN a flight session is started and a key moment is recorded
        await FlightService.start_flight_session()
        key_moment = await FlightService.record_key_moment()

        # WHEN finishing the key moment
        finished_key_moment = await FlightService.finish_key_moment()

        # THEN the key moment should be finished
        self.assertEqual(finished_key_moment.pk, key_moment.pk)
        self.assertIsNotNone(finished_key_moment.ended_at)

    async def test_update_key_moment(self):
        # GIVEN a flight session is started and a key moment is recorded
        await FlightService.start_flight_session()
        key_moment = await FlightService.record_key_moment()

        # WHEN updating the key moment
        updated_name = "Updated Key Moment"
        updated_key_moment = await FlightService.update_key_moment(
            key_moment.pk, name=updated_name
        )

        # THEN the key moment should be updated
        self.assertEqual(updated_key_moment.name, updated_name)

    async def test_delete_key_moment(self):
        # GIVEN a flight session is started and a key moment is recorded
        await FlightService.start_flight_session()
        key_moment = await FlightService.record_key_moment()

        # WHEN deleting the key moment
        await FlightService.delete_key_moment(key_moment.pk)

        # THEN the key moment should be deleted
        with self.assertRaises(ValueError):
            await FlightService.update_key_moment(
                key_moment.pk, name="Should not exist"
            )

    async def test_get_key_moments_by_flight_session_id(self):
        # GIVEN a flight session is started and multiple key moments are recorded
        session = await FlightService.start_flight_session()
        key_moment_1 = await FlightService.record_key_moment()
        await FlightService.finish_key_moment()
        key_moment_2 = await FlightService.record_key_moment()

        # WHEN retrieving key moments by flight session ID
        key_moments = await FlightService.get_key_moments_by_flight_session_id(
            session.pk
        )

        # THEN the correct number of key moments should be retrieved
        self.assertEqual(len(key_moments), 2)
        self.assertIn(key_moment_1, key_moments)
        self.assertIn(key_moment_2, key_moments)

    async def test_start_flight_session(self):
        initial_count = await FlightSession.objects.acount()

        await FlightService.start_flight_session()

        self.assertEqual(await FlightSession.objects.acount(), initial_count + 1)

    async def test_start_flight_session_when_existing(self):
        # GIVEN that a flight session already exists that is currently in
        #       progress (by default, it won't have `ended_at`)
        await FlightSession.objects.acreate()

        # WHEN trying to start another flight session
        # THEN an error will occur
        with self.assertRaises(ValueError):
            await FlightService.start_flight_session()

    async def test_end_flight_session(self):
        # GIVEN that a flight session was started
        created = await FlightService.start_flight_session()

        # WHEN ending the flight session
        ended = await FlightService.end_flight_session()

        # THEN the flight session should be actually ended in the database
        self.assertEqual(created.pk, ended.pk)
        self.assertTrue(created.is_active)
        await created.arefresh_from_db()
        self.assertFalse(created.is_active)
