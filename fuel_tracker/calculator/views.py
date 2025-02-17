from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from fuel_tracker.calculator.cache_manager import FuelCalculationCache
from fuel_tracker.calculator.config_manager import ConfigurationManager
from fuel_tracker.calculator.models import Airplane
from fuel_tracker.calculator.models import Configuration
from fuel_tracker.calculator.models import FuelCalculationRecord
from fuel_tracker.calculator.serializers import AirplaneSerializer
from fuel_tracker.calculator.serializers import ConfigurationSerializer
from fuel_tracker.calculator.serializers import FuelCalculationSerializer
from fuel_tracker.calculator.services import FuelCalculationService


class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = Configuration.objects.all()
    http_method_names = ["get", "post", "head"]  # Disable PUT/PATCH/DELETE
    serializer_class = ConfigurationSerializer

    def get_queryset(self):
        return self.queryset.order_by("-created_at")[:1]  # pyright: ignore [reportOptionalMemberAccess]


class FuelCalculationRecordModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelCalculationRecord
        fields = "__all__"
        depth = 1


class FuelCalculationRecordViewSet(viewsets.ModelViewSet):
    queryset = FuelCalculationRecord.objects.all()
    http_method_names = ["get"]
    serializer_class = FuelCalculationRecordModelSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calculation_service = FuelCalculationService()
        self.cache_manager = FuelCalculationCache()
        self.config_manager = ConfigurationManager()

    @extend_schema(request=FuelCalculationSerializer, methods=["POST"])
    @action(detail=True, methods=["post"])
    def calculate_fuel(self, request, pk=None):
        airplane = self.get_object()
        serializer = FuelCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Validate input
            if serializer.validated_data["passengers"] > airplane.max_passengers:
                return Response(
                    {
                        "error": f"Exceeds max passengers ({airplane.max_passengers})",
                    },
                    status=400,
                )

            # Get and validate config
            config = self.config_manager.get_merged_config(
                serializer.validated_data.get("config_override", {}),
            )
            self.config_manager.validate_config(config)

            # Check cache
            cache_key = self.cache_manager.generate_key(
                airplane.airplane_id,
                serializer.validated_data["passengers"],
                config,
            )
            if cached := self.cache_manager.get(cache_key):
                return Response(cached)

            # Calculate
            result = self.calculation_service.calculate(
                airplane.airplane_id,
                serializer.validated_data["passengers"],
                config,
            )

            # Save record
            FuelCalculationRecord.objects.create(
                airplane=airplane,
                passengers=serializer.validated_data["passengers"],
                fuel_capacity=result["fuel_capacity"],
                fuel_consumption_per_minute=result["fuel_consumption_per_minute"],
                flight_duration=result["flight_duration"],
                time_unit=config["time_unit"],
                configuration_snapshot=config,
            )

            # Cache result
            self.cache_manager.set(cache_key, result)

            return Response(result)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
