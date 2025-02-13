from django.core.validators import MinValueValidator
from django.db import models


class Configuration(models.Model):
    LOG_BASE_CHOICES = [
        ("10", "Base 10"),
        ("e", "Natural Logarithm"),
    ]
    TIME_UNIT_CHOICES = [
        ("minute", "Minute"),
        ("hour", "Hour"),
        ("day", "Day"),
    ]

    fuel_capacity_multiplier = models.FloatField(default=200.0)
    log_base = models.CharField(
        max_length=2,
        choices=LOG_BASE_CHOICES,
        default="10",
    )
    passenger_fuel_impact = models.FloatField(default=0.002)
    fuel_consumption_coefficient = models.FloatField(default=0.80)
    time_unit = models.CharField(
        max_length=10,
        choices=TIME_UNIT_CHOICES,
        default="minute",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "created_at"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            "Configuration: "
            f"fuel_capacity_multiplier: {self.fuel_capacity_multiplier}, "
            f"log_base: {self.log_base}"
            f"passenger_fuel_impact: {self.passenger_fuel_impact}, "
            "fuel_consumption_coefficient: "
            f"{self.fuel_consumption_coefficient}, "
            f"time_unit: {self.time_unit}, "
            f"created_at: {self.created_at}"
        )


class Airplane(models.Model):
    airplane_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    max_passengers = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    def __str__(self) -> str:
        return f"Airplane: {self.airplane_id} - {self.name}"


class FuelCalculationRecord(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    passengers = models.PositiveIntegerField()
    fuel_capacity = models.FloatField()
    fuel_consumption_per_minute = models.FloatField()
    flight_duration = models.FloatField()
    time_unit = models.CharField(max_length=10)
    configuration_snapshot = models.JSONField()

    def __str__(self) -> str:
        return (
            "FuelCalculationRecord: "
            f"airplane: {self.airplane}, "
            f"passengers: {self.passengers}, "
            f"fuel_capacity: {self.fuel_capacity}, "
            "fuel_consumption_per_minute: "
            f"{self.fuel_consumption_per_minute}, "
            f"flight_duration: {self.flight_duration}, "
            f"time_unit: {self.time_unit}, "
            f"timestamp: {self.timestamp}"
        )
