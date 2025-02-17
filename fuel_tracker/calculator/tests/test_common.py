from datetime import datetime
from http import HTTPStatus
from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from fuel_tracker.calculator.models import Airplane
from fuel_tracker.calculator.models import Configuration
from fuel_tracker.calculator.models import FuelCalculationRecord
from fuel_tracker.calculator.views import AirplaneViewSet
from fuel_tracker.calculator.views import FuelCalculationSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def config():
    return Configuration.objects.create(
        fuel_capacity_multiplier=200.0,
        log_base="10",
        passenger_fuel_impact=0.002,
        fuel_consumption_coefficient=0.80,
        time_unit="minute",
    )


@pytest.fixture
def airplane():
    return Airplane.objects.create(
        airplane_id=1,
        name="Test Airplane",
        max_passengers=100,
    )


@pytest.fixture
def fuel_record(airplane):
    return FuelCalculationRecord.objects.create(
        airplane=airplane,
        passengers=50,
        fuel_capacity=1000.0,
        fuel_consumption_per_minute=2.5,
        flight_duration=120.0,
        time_unit="minute",
        configuration_snapshot={},
    )


@pytest.fixture
def viewset():
    return AirplaneViewSet()


@pytest.mark.django_db
def test_calculate_fuel_with_no_configuration(api_factory, airplane):
    # Prepare request
    request_data = {"passengers": 50}
    request = api_factory.post(
        f"/api/airplanes/{airplane.pk}/calculate_fuel/",
        request_data,
        format="json",
    )

    view = AirplaneViewSet.as_view(actions={"post": "calculate_fuel"})

    # Execute calculation
    response = view(request, pk=airplane.pk)

    # Verify response
    assert response.status_code == HTTPStatus.OK
    assert "fuel_capacity" in response.data
    assert "fuel_consumption_per_minute" in response.data
    assert "flight_duration" in response.data
    assert "time_unit" in response.data

    # Verify default configuration values were used
    assert response.data["time_unit"] == "minute"
    assert response.data["fuel_capacity"] == 200.0  # noqa: PLR2004


@pytest.mark.django_db
def test_calculate_fuel_with_no_configuration_and_override(
    api_factory,
    airplane,
):
    # Prepare request with config override
    request_data = {
        "passengers": 50,
        "config_override": {
            "fuel_capacity_multiplier": 300.0,
            "time_unit": "hour",
        },
    }
    request = api_factory.post(
        f"/api/airplanes/{airplane.pk}/calculate_fuel/",
        request_data,
        format="json",
    )

    # Setup viewset
    view = AirplaneViewSet.as_view(actions={"post": "calculate_fuel"})

    # Execute calculation
    response = view(request, pk=airplane.pk)

    # Verify response
    assert response.status_code == HTTPStatus.OK
    assert response.data["time_unit"] == "hour"
    assert response.data["fuel_capacity"] == 300.0  # noqa: PLR2004


@pytest.mark.django_db
def test_fuel_calculation_record_str(fuel_record):
    expected_str = (
        "FuelCalculationRecord: "
        f"airplane: {fuel_record.airplane}, "
        "passengers: 50, "
        "fuel_capacity: 1000.0, "
        "fuel_consumption_per_minute: 2.5, "
        "flight_duration: 120.0, "
        "time_unit: minute, "
        f"timestamp: {fuel_record.timestamp}"
    )
    assert str(fuel_record) == expected_str


class TestConfigurationModel:
    def test_configuration_creation(self):
        default_fuel_capacity_multiplier = 200.0

        config = Configuration.objects.create(
            fuel_capacity_multiplier=default_fuel_capacity_multiplier,
            log_base="10",
            passenger_fuel_impact=0.002,
            fuel_consumption_coefficient=0.80,
            time_unit="minute",
        )
        assert config.fuel_capacity_multiplier == default_fuel_capacity_multiplier
        assert config.log_base == "10"
        assert isinstance(config.created_at, datetime)

    def test_configuration_str_representation(self):
        config = Configuration.objects.create()
        assert str(config).startswith("Configuration:")


class TestAirplaneModel:
    def test_airplane_creation(self):
        default_max_passengers = 100

        airplane = Airplane.objects.create(
            airplane_id=1,
            name="Test Airplane",
            max_passengers=default_max_passengers,
        )

        assert airplane.airplane_id == 1
        assert airplane.name == "Test Airplane"
        assert airplane.max_passengers == default_max_passengers

    def test_airplane_str_representation(self, airplane):
        assert str(airplane) == "Airplane: 1 - Test Airplane"


class TestFuelCalculationRecordModel:
    def test_fuel_calculation_record_creation(self, airplane):
        default_passengers = 50
        default_fuel_capacity = 1000.0

        record = FuelCalculationRecord.objects.create(
            airplane=airplane,
            passengers=default_passengers,
            fuel_capacity=default_fuel_capacity,
            fuel_consumption_per_minute=2.5,
            flight_duration=400.0,
            time_unit="minute",
            configuration_snapshot={},
        )
        assert record.passengers == default_passengers
        assert record.fuel_capacity == default_fuel_capacity
        assert record.airplane == airplane


class TestConfigurationViewSet:
    def test_list_configurations(self, api_client, config):
        response = api_client.get("/api/configurations/")

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1

    def test_create_configuration(self, api_client):
        data = {
            "fuel_capacity_multiplier": 250.0,
            "log_base": "e",
            "passenger_fuel_impact": 0.003,
            "fuel_consumption_coefficient": 0.85,
            "time_unit": "hour",
        }
        response = api_client.post("/api/configurations/", data)

        assert response.status_code == HTTPStatus.CREATED
        assert Configuration.objects.count() == 1


class TestAirplaneViewSet:
    @pytest.fixture(autouse=True)
    def setup(self):
        cache.clear()

    def test_calculate_fuel(self, api_client, airplane):
        data = {"passengers": 50}
        response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            data,
        )

        assert response.status_code == HTTPStatus.OK
        assert "fuel_capacity" in response.data
        assert "fuel_consumption_per_minute" in response.data
        assert "flight_duration" in response.data

    def test_calculate_fuel_invalid_passengers(
        self,
        api_client,
        airplane,
    ):
        data = {"passengers": 150}  # Exceeds max_passengers
        response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "error" in response.data

    def test_calculate_fuel_caching(self, api_client, airplane):
        data = {"passengers": 50}
        cache_key = "fuel:some_hash"

        with patch.object(
            AirplaneViewSet,
            "_generate_cache_key",
            return_value=cache_key,
        ):
            # First call
            response1 = api_client.post(
                f"/api/airplanes/{airplane.pk}/calculate_fuel/",
                data,
            )
            # Second call (should use cache)
            response2 = api_client.post(
                f"/api/airplanes/{airplane.pk}/calculate_fuel/",
                data,
            )
            assert response1.data == response2.data

    @pytest.mark.parametrize(
        (
            "time_unit",
            "expected_status",
        ),
        [
            ("minute", 200),
            ("hour", 200),
            ("day", 200),
            ("invalid", 400),
        ],
    )
    def test_calculate_fuel_time_units(
        self,
        api_client,
        airplane,
        time_unit,
        expected_status,
    ):
        data = {"passengers": 50, "config_override": {"time_unit": time_unit}}
        response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            data,
            format="json",
        )
        assert response.status_code == expected_status

    def test_calculate_fuel_different_time_units(
        self,
        api_client,
        airplane,
    ):
        base_data = {"passengers": 50}

        # Test with minutes (default)
        minute_response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            base_data,
            format="json",
        )
        assert minute_response.status_code == HTTPStatus.OK
        minute_duration = minute_response.data["flight_duration"]

        # Test with hours
        hour_data = {
            "passengers": 50,
            "config_override": {"time_unit": "hour"},
        }
        hour_response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            hour_data,
            format="json",
        )
        assert hour_response.status_code == HTTPStatus.OK
        hour_duration = hour_response.data["flight_duration"]

        # Test with days
        day_data = {"passengers": 50, "config_override": {"time_unit": "day"}}
        day_response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            day_data,
            format="json",
        )
        assert day_response.status_code == HTTPStatus.OK
        day_duration = day_response.data["flight_duration"]

        # Verify conversions
        # minute to hour (1 hour = 60 minutes)
        assert round(minute_duration / 60, 2) == round(hour_duration, 2)

        # hour to day (1 day = 24 hours)
        assert round(hour_duration / 24, 2) == round(day_duration, 2)

        # Verify fuel capacity and consumption remain the same
        assert (
            minute_response.data["fuel_capacity"] == hour_response.data["fuel_capacity"]
        )
        assert (
            minute_response.data["fuel_capacity"] == day_response.data["fuel_capacity"]
        )
        assert (
            minute_response.data["fuel_consumption_per_minute"]
            == hour_response.data["fuel_consumption_per_minute"]
        )

    @pytest.mark.parametrize(
        ("from_unit", "to_unit", "conversion_factor"),
        [
            ("minute", "hour", 1 / 60),
            ("hour", "day", 1 / 24),
            ("minute", "day", 1 / 1440),
        ],
    )
    def test_calculate_fuel_time_unit_conversions(
        self,
        api_client,
        airplane,
        from_unit,
        to_unit,
        conversion_factor,
    ):
        base_passengers = 50

        # First time unit
        first_data = {
            "passengers": base_passengers,
            "config_override": {"time_unit": from_unit},
        }
        first_response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            first_data,
            format="json",
        )

        # Second time unit
        second_data = {
            "passengers": base_passengers,
            "config_override": {"time_unit": to_unit},
        }
        second_response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            second_data,
            format="json",
        )

        # Verify conversion
        first_duration = first_response.data["flight_duration"]
        second_duration = second_response.data["flight_duration"]
        assert round(first_duration * conversion_factor, 2) == round(
            second_duration,
            2,
        )

        # Verify other values remain constant
        assert (
            first_response.data["fuel_capacity"]
            == second_response.data["fuel_capacity"]
        )
        assert (
            first_response.data["fuel_consumption_per_minute"]
            == second_response.data["fuel_consumption_per_minute"]
        )

    def test_calculate_fuel_negative_consumption(
        self,
        api_client,
        airplane,
    ):
        data = {
            "passengers": 50,
            "config_override": {
                "fuel_consumption_coefficient": -100,
                "passenger_fuel_impact": 0,
            },
        }

        response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            data,
            format="json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.data == {"error": "Fuel consumption must be positive"}

    def test_calculate_fuel_invalid_log_base(
        self,
        api_client,
        airplane,
    ):
        data = {
            "passengers": 50,
            "config_override": {
                "log_base": "bananas",
            },
        }

        response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            data,
            format="json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert (
            response.data["config_override"]["log_base"][0]
            == '"bananas" is not a valid choice.'
        )


class TestSerializers:
    @pytest.mark.parametrize(
        (
            "passengers",
            "expected_valid",
        ),
        [
            (50, True),
            (0, True),
            (-1, False),
            (None, False),
        ],
    )
    def test_fuel_calculation_serializer_validation(
        self,
        passengers,
        expected_valid,
    ):
        serializer = FuelCalculationSerializer(data={"passengers": passengers})
        assert serializer.is_valid() == expected_valid

    def test_fuel_calculation_serializer_with_config_override(self):
        data = {
            "passengers": 50,
            "config_override": {
                "fuel_capacity_multiplier": 250.0,
                "log_base": "e",
            },
        }
        serializer = FuelCalculationSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["config_override"] == {
            "fuel_capacity_multiplier": 250.0,
            "log_base": "e",
        }


@pytest.fixture
def sample_calculation_data(airplane, config):
    return {
        "airplane": airplane,
        "passengers": 50,
        "fuel_capacity": 1000.0,
        "fuel_consumption_per_minute": 2.5,
        "flight_duration": 400.0,
        "time_unit": "minute",
        "configuration_snapshot": {
            "fuel_capacity_multiplier": config.fuel_capacity_multiplier,
            "log_base": config.log_base,
            "passenger_fuel_impact": config.passenger_fuel_impact,
            "fuel_consumption_coefficient": (config.fuel_consumption_coefficient),
            "time_unit": config.time_unit,
        },
    }


class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Clear cache before each test
        cache.clear()
        # Clear all relevant database records
        FuelCalculationRecord.objects.all().delete()
        Configuration.objects.all().delete()
        Airplane.objects.all().delete()

    def test_full_calculation_workflow(
        self,
        api_client,
        airplane,
        sample_calculation_data,
    ):
        # Get initial record count
        initial_record_count = FuelCalculationRecord.objects.count()

        # Perform calculation
        response = api_client.post(
            f"/api/airplanes/{airplane.pk}/calculate_fuel/",
            {"passengers": sample_calculation_data["passengers"]},
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

        # Verify calculation record was created
        records = FuelCalculationRecord.objects.all()
        assert records.count() == initial_record_count + 1

        record = records.latest("timestamp")  # Use latest instead of last()
        assert record is not None
        assert record.airplane == airplane
        assert record.passengers == sample_calculation_data["passengers"]

        # Add more specific assertions to verify the record data
        assert record.fuel_capacity == response.data["fuel_capacity"]
        assert (
            record.fuel_consumption_per_minute
            == response.data["fuel_consumption_per_minute"]
        )
        assert record.flight_duration == response.data["flight_duration"]
        assert record.time_unit == response.data["time_unit"]


@pytest.mark.django_db
def test_calculation_with_different_configurations(client):
    # Create test airplane
    airplane = Airplane.objects.create(
        airplane_id=100,
        name="Test Airplane",
        max_passengers=200,
    )

    # First calculation without any configuration (using defaults)
    response1 = client.post(
        f"/api/airplanes/{airplane.pk}/calculate_fuel/",
        {"passengers": 100},
    )
    assert response1.status_code == HTTPStatus.OK
    result1 = response1.json()

    # Create a new configuration with different values
    Configuration.objects.create(
        fuel_capacity_multiplier=300.0,
        log_base="e",
        passenger_fuel_impact=0.003,
        fuel_consumption_coefficient=1.0,
        time_unit="hour",
    )

    # Second calculation with the new configuration
    response2 = client.post(
        f"/api/airplanes/{airplane.pk}/calculate_fuel/",
        {"passengers": 100},
    )
    assert response2.status_code == HTTPStatus.OK
    result2 = response2.json()

    # Verify that results are different
    assert result1["fuel_capacity"] != result2["fuel_capacity"]
    assert (
        result1["fuel_consumption_per_minute"] != result2["fuel_consumption_per_minute"]
    )
    assert result1["flight_duration"] != result2["flight_duration"]
    assert result1["time_unit"] != result2["time_unit"]

    # Verify specific values
    assert result1["time_unit"] == "minute"
    assert result2["time_unit"] == "hour"
