from channels.layers import get_channel_layer

from whitebox import WebsocketEventHandler
from whitebox_plugin_flight_management.services import FlightService
from whitebox_plugin_flight_management.serializers import (
    FlightSessionSerializer,
)


channel_layer = get_channel_layer()


def serialize_flight_session(session):
    """
    Serialize the flight session for sending over WebSocket.
    """
    return FlightSessionSerializer(instance=session).data


class FlightStartHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.start` event.
    """

    default_callbacks = [
        lambda data, ctx: channel_layer.group_send(
            "flight",
            {
                "type": "flight.start",
                "flight_session": serialize_flight_session(ctx["flight_session"]),
            },
        )
    ]

    async def handle(self, data):
        session = await FlightService.start_flight_session(
            data.get("name"),
        )

        return {
            "flight_session": session,
        }

    async def return_message(self):
        """
        Return a message to be sent over the WebSocket.
        This method should be implemented by subclasses.
        """
        return {
            "type": "message",
            "message": "Flight started, enjoy your flight!",
        }


class FlightEndHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.end` event.
    """

    default_callbacks = [
        lambda data, ctx: channel_layer.group_send(
            "flight",
            {
                "type": "flight.end",
                "flight_session": serialize_flight_session(ctx["flight_session"]),
            },
        )
    ]

    async def handle(self, data):
        session = await FlightService.end_flight_session()
        return {
            "flight_session": session,
        }

    async def return_message(self):
        """
        Return a message to be sent over the WebSocket.
        This method should be implemented by subclasses.
        """
        return {
            "type": "message",
            "message": "Flight ended.",
        }
