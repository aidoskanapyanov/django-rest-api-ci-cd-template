import math
from dataclasses import dataclass
from typing import Any


@dataclass
class FuelCalculationService:
    def calculate(
        self,
        airplane_id: int,
        passengers: int,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        fuel_capacity = self._calculate_fuel_capacity(airplane_id, config)
        consumption = self._calculate_consumption(
            airplane_id,
            passengers,
            config,
        )
        duration = self._calculate_duration(
            fuel_capacity,
            consumption,
            config["time_unit"],
        )

        return {
            "fuel_capacity": round(fuel_capacity, 2),
            "fuel_consumption_per_minute": round(consumption, 4),
            "flight_duration": round(duration, 2),
            "time_unit": config["time_unit"],
        }

    def _calculate_fuel_capacity(
        self,
        airplane_id: int,
        config: dict[str, Any],
    ) -> float:
        return config["fuel_capacity_multiplier"] * airplane_id

    def _calculate_consumption(
        self,
        airplane_id: int,
        passengers: int,
        config: dict[str, Any],
    ) -> float:
        log_value = (
            math.log(airplane_id)
            if config["log_base"] == "e"
            else math.log(airplane_id, 10)
        )
        consumption = (
            log_value * config["fuel_consumption_coefficient"]
            + passengers * config["passenger_fuel_impact"]
        )

        if consumption <= 0:
            msg = "Fuel consumption must be positive"
            raise ValueError(msg)
        return consumption

    def _calculate_duration(
        self,
        capacity: float,
        consumption: float,
        time_unit: str,
    ) -> float:
        unit_conversion = {
            "minute": 1,
            "hour": 1 / 60,
            "day": 1 / 1440,
        }
        max_minutes = capacity / consumption
        return max_minutes * unit_conversion.get(time_unit, 1)
