from asgiref.sync import sync_to_async

from django.utils import timezone

from utils.locking import global_lock
from .models import FlightSession, KeyMoment
from .serializers import KeyMomentSerializer


class FlightService:
    @classmethod
    def _get_queryset_with_prefetches(cls):
        return (
            FlightSession.objects.prefetch_related("recordings")
            .prefetch_related("key_moments")
            .all()
        )

    @classmethod
    def _lock(cls):
        # Convenience method to create a lock object, as it is not reusable
        return global_lock("flight_management_lock")

    # region flight sessions

    @classmethod
    @sync_to_async
    def start_flight_session(cls, name=None):
        """
        Start a new flight session.

        This method initiates a flight session, triggering any registered
        callbacks or actions associated with the flight start event.

        Raises:
            ValueError: If a flight session is already in progress.

        Returns:make
            FlightSession: The newly created flight session.
        """
        name = name or "Unnamed Flight Session"

        with cls._lock():
            current = cls._get_queryset_with_prefetches().current()
            if current:
                raise ValueError("A flight session is already in progress.")

            session = FlightSession.objects.create(
                name=name,
            )
            session._prefetched_objects_cache = {
                "recordings": [],
                "key_moments": [],
            }

        return session

    @classmethod
    @sync_to_async
    def end_flight_session(cls):
        """
        End the current flight session.

        This method concludes the flight session, marking it as ended and
        triggering any registered callbacks or actions associated with the
        flight end event.

        Raises:
            ValueError: If no flight session is currently in progress.

        Returns:
            FlightSession: The ended flight session.
        """
        with cls._lock():
            current = cls._get_queryset_with_prefetches().current()
            if not current:
                raise ValueError("No flight session is currently in progress.")

            current.ended_at = timezone.now()
            current.save()

        return current

    @classmethod
    @sync_to_async
    def get_current_flight_session(cls):
        """
        Retrieve the current flight session.

        Returns:
            FlightSession: The current flight session if it exists, otherwise None.
        """
        with cls._lock():
            return cls._get_queryset_with_prefetches().current()

    @classmethod
    async def get_flight_session_by_id(cls, session_id):
        """
        Retrieve a flight session by its ID.

        Args:
            session_id (int): The ID of the flight session to retrieve.

        Returns:
            FlightSession: The flight session with the specified ID, or None if not found.
        """
        return await cls._get_queryset_with_prefetches().filter(id=session_id).afirst()

    # endregion flight sessions

    # region key moments

    @classmethod
    @sync_to_async
    def record_key_moment(cls):
        with cls._lock():
            flight_session = FlightSession.objects.prefetch_related(
                "key_moments"
            ).current()
            if not flight_session:
                raise ValueError("No flight session is currently in progress.")

            key_moment = flight_session.key_moments.current()
            if key_moment:
                raise ValueError("A key moment is already being recorded.")

            key_moment_count = flight_session.key_moments.count()
            key_moment_index = key_moment_count + 1

            key_moment = flight_session.key_moments.create(
                name=f"Key Moment #{key_moment_index}",
            )

        return key_moment

    @classmethod
    @sync_to_async
    def finish_key_moment(cls):
        with cls._lock():
            flight_session = FlightSession.objects.prefetch_related(
                "key_moments"
            ).current()
            if not flight_session:
                raise ValueError("No flight session is currently in progress.")

            key_moment = flight_session.key_moments.current()
            if not key_moment:
                raise ValueError("No key moment is currently being recorded.")

            key_moment.ended_at = timezone.now()
            key_moment.save()

        return key_moment

    @classmethod
    async def update_key_moment(cls, key_moment_id, **updates):
        key_moment = await KeyMoment.objects.filter(pk=key_moment_id).afirst()
        if not key_moment:
            raise ValueError(f"Key moment with ID: {key_moment_id} not found")

        s = KeyMomentSerializer(
            instance=key_moment,
            data=updates,
            partial=True,
        )

        if not s.is_valid():
            raise ValueError(s.errors)

        data = s.validated_data
        # Not using `s.save()` here as it does not support `update_fields`,
        # causing the entire model to be effectively rewritten, so with this
        # approach we won't have race conditions among different users. This
        # will be improved with WhiteboxInterfaceModelSerializer implementation
        await KeyMoment.objects.filter(pk=key_moment_id).aupdate(**data)

        await key_moment.arefresh_from_db()
        return key_moment

    @classmethod
    async def delete_key_moment(cls, key_moment_id):
        key_moment = await KeyMoment.objects.filter(pk=key_moment_id).afirst()
        if not key_moment:
            raise ValueError(f"Key moment with ID: {key_moment_id} not found")

        await key_moment.adelete()
        return key_moment

    @classmethod
    async def get_key_moments_by_flight_session_id(cls, flight_session_id):
        qs = KeyMoment.objects.filter(
            flight_session_id=flight_session_id,
        )

        # Evaluate the queryset immediately so that a list is returned
        results = [entry async for entry in qs]
        return results

    # endregion key moments
