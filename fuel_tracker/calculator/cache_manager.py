import hashlib
import json
from typing import Any

from django.core.cache import cache


class FuelCalculationCache:
    def get(self, key: str) -> dict[str, Any] | None:
        return cache.get(key)

    def set(
        self,
        key: str,
        value: dict[str, Any],
        timeout: int = 3600,
    ) -> None:
        cache.set(key, value, timeout=timeout)

    def generate_key(
        self,
        airplane_id: int,
        passengers: int,
        config: dict[str, Any],
    ) -> str:
        params = {
            "airplane_id": airplane_id,
            "passengers": passengers,
            "time_unit": config["time_unit"],
            **{k: v for k, v in config.items() if k != "time_unit"},
        }
        encoded_params = json.dumps(params, sort_keys=True).encode()
        return f"fuel:{hashlib.md5(encoded_params).hexdigest()}"  # noqa: S324
