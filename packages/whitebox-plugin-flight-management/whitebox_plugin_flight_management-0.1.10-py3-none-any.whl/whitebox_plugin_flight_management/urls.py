from rest_framework.routers import SimpleRouter

from .views import (
    FlightSessionViewSet,
)


app_name = "whitebox_plugin_flight_management"


router = SimpleRouter()


router.register(
    r"flight-sessions",
    FlightSessionViewSet,
    basename="flight-session",
)

urlpatterns = router.urls
