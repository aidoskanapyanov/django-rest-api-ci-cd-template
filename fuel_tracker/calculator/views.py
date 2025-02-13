import hashlib
import json
import math

from django.core.cache import cache
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from fuel_tracker.calculator.models import Airplane
from fuel_tracker.calculator.models import Configuration
from fuel_tracker.calculator.models import FuelCalculationRecord


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        model = Configuration
        fields = "__all__"
        read_only_fields = ("created_at",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        model = Airplane
        fields = "__all__"


class FuelCalculationSerializer(serializers.Serializer):
    passengers = serializers.IntegerField(min_value=0)
    config_override = serializers.JSONField(required=False, default=dict)


class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = Configuration.objects.all()
    http_method_names = ["get", "post", "head"]  # Disable PUT/PATCH/DELETE
    serializer_class = ConfigurationSerializer

    def get_queryset(self):
        return self.queryset.order_by("-created_at")[:1]  # pyright: ignore [reportOptionalMemberAccess]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    @action(detail=True, methods=["post"])
    def calculate_fuel(self, request, pk=None):
        airplane = self.get_object()
        serializer = FuelCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get latest configuration
        try:
            config = Configuration.objects.latest()
        except Configuration.DoesNotExist:
            config = Configuration()

        # Merge with override
        merged_config = {
            "fuel_capacity_multiplier": config.fuel_capacity_multiplier,
            "log_base": config.log_base,
            "passenger_fuel_impact": config.passenger_fuel_impact,
            "fuel_consumption_coefficient": config.fuel_consumption_coefficient,
            "time_unit": config.time_unit,
        }
        merged_config.update(serializer.validated_data.get("config_override", {}))

        # Validate merged config
        if merged_config["log_base"] not in ["10", "e"]:
            return Response({"error": "Invalid log base"}, status=400)

        # Validate time_unit
        valid_time_units = ["minute", "hour", "day"]
        if merged_config["time_unit"] not in valid_time_units:
            return Response({"error": "Invalid time unit"}, status=400)

        # Validate passengers
        passengers = serializer.validated_data["passengers"]
        if passengers > airplane.max_passengers:
            return Response(
                {"error": f"Exceeds max passengers ({airplane.max_passengers})"},
                status=400,
            )

        # Generate cache key
        cache_key = self._generate_cache_key(
            airplane.airplane_id,
            passengers,
            merged_config,
        )

        # Check cache
        if cached := cache.get(cache_key):
            return Response(cached)

        # Perform calculation
        try:
            result = self._perform_calculation(
                airplane.airplane_id,
                passengers,
                merged_config,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        # Save to history
        FuelCalculationRecord.objects.create(
            airplane=airplane,
            passengers=passengers,
            fuel_capacity=result["fuel_capacity"],
            fuel_consumption_per_minute=result["fuel_consumption_per_minute"],
            flight_duration=result["flight_duration"],
            time_unit=merged_config["time_unit"],
            configuration_snapshot=merged_config,
        )

        # Cache result
        cache.set(cache_key, result, timeout=3600)

        return Response(result)

    def _generate_cache_key(self, airplane_id, passengers, config):
        params = {
            "airplane_id": airplane_id,
            "passengers": passengers,
            "time_unit": config["time_unit"],  # Add time_unit to cache key
            **{k: v for k, v in config.items() if k != "time_unit"},
        }
        return f"fuel:{
            hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        }"  # noqa: S324

    def _perform_calculation(self, airplane_id, passengers, config):
        # Calculate fuel capacity
        fuel_capacity = config["fuel_capacity_multiplier"] * airplane_id

        # Calculate log value
        if config["log_base"] == "e":
            log_value = math.log(airplane_id)
        else:
            log_value = math.log(airplane_id, 10)

        # Calculate consumption per minute
        fuel_consumption_per_minute = (
            log_value * config["fuel_consumption_coefficient"]
            + passengers * config["passenger_fuel_impact"]
        )

        if fuel_consumption_per_minute <= 0:
            msg = "Fuel consumption must be positive"
            raise ValueError(msg)

        # Calculate flight duration in minutes
        max_minutes = fuel_capacity / fuel_consumption_per_minute

        # Convert to requested unit
        unit_conversion = {
            "minute": 1,
            "hour": 1 / 60,  # Convert minutes to hours
            "day": 1 / 1440,  # Convert minutes to days
        }

        flight_duration = max_minutes * unit_conversion.get(config["time_unit"], 1)

        return {
            "fuel_capacity": round(fuel_capacity, 2),
            "fuel_consumption_per_minute": round(fuel_consumption_per_minute, 4),
            "flight_duration": round(flight_duration, 2),
            "time_unit": config[
                "time_unit"
            ],  # Make sure to use the merged config time_unit
        }
