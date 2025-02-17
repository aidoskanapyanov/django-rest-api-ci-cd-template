from rest_framework import serializers

from fuel_tracker.calculator.models import Airplane
from fuel_tracker.calculator.models import Configuration


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        model = Configuration
        fields = "__all__"
        read_only_fields = ("created_at",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        model = Airplane
        fields = "__all__"


class ConfigOverrideSerializer(serializers.Serializer):
    fuel_capacity_multiplier = serializers.FloatField(required=False)
    log_base = serializers.ChoiceField(choices=["10", "e"], required=False)
    passenger_fuel_impact = serializers.FloatField(required=False)
    fuel_consumption_coefficient = serializers.FloatField(required=False)
    time_unit = serializers.ChoiceField(
        choices=["minute", "hour", "day"],
        required=False,
    )


class FuelCalculationSerializer(serializers.Serializer):
    passengers = serializers.IntegerField(min_value=0)
    config_override = ConfigOverrideSerializer(required=False)
