from rest_framework import serializers

from .models import (
    FlightSession,
    FlightSessionRecording,
    KeyMoment,
)


class FlightSessionRecordingSerializer(serializers.ModelSerializer):
    provided_by = serializers.CharField(source="get_provider")

    class Meta:
        model = FlightSessionRecording
        fields = [
            "id",
            "created_at",
            "file",
            "status",
            "provided_by",
            "provided_by_id",
        ]
        extra_kwargs = {
            "file": {
                "source": "get_file_url",
            },
        }


class KeyMomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyMoment
        fields = [
            "id",
            "flight_session_id",
            "name",
            "started_at",
            "ended_at",
        ]
        # TODO: Create WhiteboxInterfaceModelSerializer that will have an
        #       overridable `fields_allow_edit: list` instead, to be exposed to
        #       the websocket operations and later allow multi-user-type
        #       granular permissions, and be `partial=True` by default
        read_only_fields = [
            "id",
            "flight_session_id",
            "started_at",
            "ended_at",
        ]


class EmbedFlightSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightSession
        fields = [
            "id",
            "name",
            "started_at",
            "ended_at",
        ]


class FlightSessionSerializer(EmbedFlightSessionSerializer):
    recordings = FlightSessionRecordingSerializer(many=True)
    key_moments = KeyMomentSerializer(many=True)

    class Meta(EmbedFlightSessionSerializer.Meta):
        fields = [
            *EmbedFlightSessionSerializer.Meta.fields,
            "recordings",
            "key_moments",
        ]
