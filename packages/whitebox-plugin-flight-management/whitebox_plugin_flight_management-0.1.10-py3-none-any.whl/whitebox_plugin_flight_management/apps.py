from django.apps.config import AppConfig

from plugin.registry import model_registry


class WhiteboxPluginFlightManagementConfig(AppConfig):
    name = "whitebox_plugin_flight_management"
    verbose_name = "Whitebox Plugin Flight Management"

    def ready(self):
        from .models import FlightSession, FlightSessionRecording

        model_registry.register("flight.FlightSession", FlightSession)
        model_registry.register(
            "flight.FlightSessionRecording",
            FlightSessionRecording,
        )
