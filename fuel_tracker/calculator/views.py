from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
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
from fuel_tracker.calculator.serializers import FuelCalculationRecordModelSerializer
from fuel_tracker.calculator.serializers import FuelCalculationSerializer
from fuel_tracker.calculator.serializers import ResultSerializer
from fuel_tracker.calculator.services import FuelCalculationService


@extend_schema_view(
    list=extend_schema(
        description="""
        Returns the most recent configuration settings.
        Only returns a single configuration record, ordered by creation date.

        By default:
        - fuel_capacity_multiplier=200.0
        - log_base='10'
        - passenger_fuel_impact=0.002
        - fuel_consumption_coefficient=0.80
        - time_unit='minute' are used.
        """,
    ),
    create=extend_schema(
        description="Creates a new configuration with custom parameters "
        "for fuel calculations. Previous configurations "
        "are retained but not used.",
    ),
    retrieve=extend_schema(
        description="Returns a specific configuration by ID.",
    ),
)
class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = Configuration.objects.all()
    http_method_names = ["get", "post", "head"]  # Disable PUT/PATCH/DELETE
    serializer_class = ConfigurationSerializer

    def get_queryset(self):
        return self.queryset.order_by("-created_at")[:1]  # pyright: ignore [reportOptionalMemberAccess]


@extend_schema_view(
    list=extend_schema(
        description=("Returns a list of all historical fuel calculation records."),
    ),
    retrieve=extend_schema(
        description="Returns a specific fuel calculation record by ID, "
        "including the airplane details and configuration snapshot used.",
    ),
)
class FuelCalculationRecordViewSet(viewsets.ModelViewSet):
    queryset = FuelCalculationRecord.objects.all()
    http_method_names = ["get"]
    serializer_class = FuelCalculationRecordModelSerializer


@extend_schema_view(
    list=extend_schema(
        description=("Returns a list of all registered airplanes in the system."),
    ),
    create=extend_schema(
        description="Creates a new airplane with a unique ID and maximum "
        "passenger capacity.",
    ),
    retrieve=extend_schema(
        description="Returns a specific airplane's details by ID.",
    ),
    update=extend_schema(
        description="Updates all fields of an existing airplane.",
    ),
    partial_update=extend_schema(
        description="Partially updates an existing airplane's fields.",
    ),
    destroy=extend_schema(description="Removes an airplane from the system."),
)
class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calculation_service = FuelCalculationService()
        self.cache_manager = FuelCalculationCache()
        self.config_manager = ConfigurationManager()

    @extend_schema(
        request=FuelCalculationSerializer,
        responses={
            201: OpenApiResponse(
                response=ResultSerializer,
                description="Calculation result",
            ),
            400: OpenApiResponse(description="Bad request"),
        },
        methods=["POST"],
        description="""
        Calculates fuel metrics for a specific airplane.

        Computes:
        - Fuel tank capacity (based on airplane ID)
        - Fuel consumption per minute (based on passenger count
          and airplane ID)
        - Maximum flight duration

        The calculation uses either the default configuration or custom
        overrides provided in the request. Results are cached for identical
        input parameters.

        Returns HTTP 400 if:
        - Passenger count exceeds airplane's maximum capacity
        - Configuration validation fails
        - Calculation parameters are invalid
        """,
    )
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
