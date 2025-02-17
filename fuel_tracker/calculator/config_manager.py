from typing import Any

from fuel_tracker.calculator.models import Configuration


class ConfigurationManager:
    VALID_LOG_BASES = ["10", "e"]
    VALID_TIME_UNITS = ["minute", "hour", "day"]

    def get_merged_config(
        self,
        override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        config = self._get_latest_config()
        merged = {
            "fuel_capacity_multiplier": config.fuel_capacity_multiplier,
            "log_base": config.log_base,
            "passenger_fuel_impact": config.passenger_fuel_impact,
            "fuel_consumption_coefficient": config.fuel_consumption_coefficient,
            "time_unit": config.time_unit,
        }
        if override:
            merged.update(override)
        return merged

    def validate_config(self, config: dict[str, Any]) -> None:
        if config["log_base"] not in self.VALID_LOG_BASES:
            msg = "Invalid log base"
            raise ValueError(msg)
        if config["time_unit"] not in self.VALID_TIME_UNITS:
            msg = "Invalid time unit"
            raise ValueError(msg)

    def _get_latest_config(self) -> Configuration:
        try:
            return Configuration.objects.latest()
        except Configuration.DoesNotExist:
            return Configuration()
