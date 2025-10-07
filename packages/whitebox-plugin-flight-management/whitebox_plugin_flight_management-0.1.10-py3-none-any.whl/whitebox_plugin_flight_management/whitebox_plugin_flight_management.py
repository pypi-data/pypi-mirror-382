from whitebox import Plugin
from .handlers import (
    FlightStartHandler,
    FlightEndHandler,
    KeyMomentRecordHandler,
    KeyMomentFinishHandler,
    KeyMomentUpdateHandler,
    KeyMomentDeleteHandler,
)


class WhiteboxPluginFlightManagement(Plugin):
    name = "Flight Management"

    provides_capabilities = [
        "flight-management",
    ]
    slot_component_map = {
        "flight-management.trigger-button": "TriggerButton",
    }
    exposed_component_map = {
        "service-component": {
            "flight-service": "FlightServiceComponent",
        },
        "flight-management": {
            "trigger-button": "TriggerButton",
        },
    }

    plugin_event_map = {
        "flight.start": FlightStartHandler,
        "flight.end": FlightEndHandler,
        "flight.key_moment.record": KeyMomentRecordHandler,
        "flight.key_moment.finish": KeyMomentFinishHandler,
        "flight.key_moment.update": KeyMomentUpdateHandler,
        "flight.key_moment.delete": KeyMomentDeleteHandler,
    }

    state_store_map = {
        "flight.inputs": "stores/inputs",
        "flight.mission-control": "stores/mission_control",
    }

    plugin_url_map = {
        "flight.flight-session-list": "whitebox_plugin_flight_management:flight-session-list",
    }

    def get_plugin_classes_map(self):
        from .services import FlightService
        from .serializers import (
            FlightSessionSerializer,
            KeyMomentSerializer,
        )

        return {
            "flight.FlightService": FlightService,
            "flight.FlightSessionSerializer": FlightSessionSerializer,
            "flight.KeyMomentSerializer": KeyMomentSerializer,
        }


plugin_class = WhiteboxPluginFlightManagement
