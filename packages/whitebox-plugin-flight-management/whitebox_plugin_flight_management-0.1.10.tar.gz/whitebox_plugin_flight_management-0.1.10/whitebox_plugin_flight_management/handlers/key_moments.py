from channels.layers import get_channel_layer

from whitebox import WebsocketEventHandler
from whitebox_plugin_flight_management.services import FlightService
from whitebox_plugin_flight_management.serializers import (
    KeyMomentSerializer,
)


channel_layer = get_channel_layer()


def serialize_key_moment(key_moment):
    """
    Serialize the key moment for sending over WebSocket.
    """
    return KeyMomentSerializer(instance=key_moment).data


def emit_key_moment_callback(event_type):
    async def callback(data, ctx):
        await channel_layer.group_send(
            "flight",
            {
                "type": event_type,
                "key_moment": serialize_key_moment(ctx["key_moment"]),
            },
        )

    return callback


class KeyMomentRecordHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.key_moment.record` event.
    """

    default_callbacks = [
        emit_key_moment_callback("flight.key_moment.record"),
    ]

    async def handle(self, data):
        key_moment = await FlightService.record_key_moment()
        return {
            "key_moment": key_moment,
        }

    async def return_message(self):
        return {
            "type": "message",
            "message": "Key moment now recording.",
        }


class KeyMomentFinishHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.key_moment.finish` event.
    """

    default_callbacks = [
        emit_key_moment_callback("flight.key_moment.finish"),
    ]

    async def handle(self, data):
        key_moment = await FlightService.finish_key_moment()
        return {
            "key_moment": key_moment,
        }

    async def return_message(self):
        return {
            "type": "message",
            "message": "Key moment recorded.",
        }


class KeyMomentUpdateHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.key_moment.update` event.
    """

    default_callbacks = [
        emit_key_moment_callback("flight.key_moment.update"),
    ]

    async def handle(self, data):
        key_moment_id = data.pop("key_moment_id")

        key_moment = await FlightService.update_key_moment(
            key_moment_id=key_moment_id,
            **data,
        )

        return {
            "key_moment": key_moment,
        }

    async def return_message(self):
        return {
            "type": "message",
            "message": "Key moment updated.",
        }


class KeyMomentDeleteHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.key_moment.delete` event.
    """

    default_callbacks = [
        lambda data, ctx: channel_layer.group_send(
            "flight",
            {
                "type": "flight.key_moment.delete",
                "flight_session_id": ctx["flight_session_id"],
                "key_moment_id": ctx["key_moment_id"],
            },
        )
    ]

    async def handle(self, data):
        key_moment_id = data.pop("key_moment_id")

        deleted = await FlightService.delete_key_moment(
            key_moment_id=key_moment_id,
        )

        return {
            "flight_session_id": deleted.flight_session_id,
            "key_moment_id": key_moment_id,
        }

    async def return_message(self):
        return {
            "type": "message",
            "message": "Key moment deleted.",
        }
