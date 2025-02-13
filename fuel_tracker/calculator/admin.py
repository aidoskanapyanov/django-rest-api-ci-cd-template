from django.contrib import admin

from fuel_tracker.calculator.models import Airplane
from fuel_tracker.calculator.models import Configuration
from fuel_tracker.calculator.models import FuelCalculationRecord


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "fuel_capacity_multiplier", "log_base")
    ordering = ("-created_at",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("airplane_id", "name", "max_passengers")


@admin.register(FuelCalculationRecord)
class FuelCalculationRecordAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "airplane", "passengers", "flight_duration")
