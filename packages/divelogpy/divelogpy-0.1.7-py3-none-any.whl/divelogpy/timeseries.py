"""Time series helpers for decoded dive samples."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, List, Mapping, Sequence, Tuple

try:  # optional dependency
    import pandas as _pd
except ImportError:  # pragma: no cover - handled dynamically
    _pd = None


_SENTINEL_PRESSURES = {0, 65535, 65534}


def _normalize_pressure(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        if value in _SENTINEL_PRESSURES:
            return None
        return float(value) * 2.0
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            numeric = float(stripped)
        except ValueError:
            return None
        if numeric in _SENTINEL_PRESSURES:
            return None
        return numeric * 2.0
    return None


@dataclass
class DiveTimeSeries:
    """Expose decoded sample metrics with DataFrame helpers."""

    samples: Sequence[dict]
    raw_records: Sequence[bytes]
    tank_alias_map: Mapping[str, Tuple[str, str]] | None = None
    tank_display_order: Tuple[Tuple[str, str], ...] = tuple()

    @property
    def available_fields(self) -> Sequence[str]:
        if not self.samples:
            return []
        keys = set()
        for sample in self.samples:
            keys.update(sample.keys())
            extension = sample.get("extension")
            if isinstance(extension, dict):
                keys.update(f"extension.{name}" for name in extension.keys())
        return sorted(keys)

    def to_df(self, fields: Iterable[str] | None = None, *, include_time: bool = True):
        """Return a DataFrame with the requested metric fields.

        Parameters
        ----------
        fields:
            Iterable of metric names. Supports dot-notation for extension values,
            e.g. ``extension.hp_o2_pressure``. When omitted, all available fields
            are included.
        include_time:
            Whether to include the ``time_seconds`` column (if present) as the
            first column.
        """

        if _pd is None:  # pragma: no cover - environment dependent
            raise RuntimeError("pandas is required for timeseries operations")

        if not self.samples:
            return _pd.DataFrame()

        all_fields = self.available_fields
        if fields is None:
            selected = [name for name in all_fields if name != "extension" and not name.startswith("extension.")]
            extension_fields = [name for name in all_fields if name.startswith("extension.")]
            selected.extend(extension_fields)
        else:
            selected = list(fields)

        rows: List[dict] = []
        for sample in self.samples:
            row: dict = {}
            if include_time and "time_seconds" in sample:
                row["time_seconds"] = sample["time_seconds"]
            for field in selected:
                if field.startswith("extension."):
                    _, key = field.split(".", 1)
                    ext = sample.get("extension") or {}
                    row[field] = ext.get(key)
                else:
                    row[field] = sample.get(field)
            rows.append(row)

        df = _pd.DataFrame(rows)
        if include_time and "time_seconds" in df.columns:
            df = df.set_index("time_seconds")
        return df

    def __getattr__(self, name: str):
        if name in {"samples", "raw_records"}:
            return super().__getattribute__(name)
        if name not in self.available_fields:
            raise AttributeError(name)
        return self.to_df([name])

    @property
    def available_tanks(self) -> Sequence[str]:
        """Return human-friendly tank names discovered in the samples."""

        return [name for name, _ in self.tank_display_order]

    def get_tank_data(self, tank_name: str):
        """Return a DataFrame of pressure samples for *tank_name*.

        The lookup accepts the user-visible transmitter name (e.g. ``"O2"``)
        or canonical labels like ``"tank1"``/``"tank_1"``.
        """

        if _pd is None:  # pragma: no cover - environment dependent
            raise RuntimeError("pandas is required for timeseries operations")

        if not self.tank_alias_map:
            raise KeyError("No wireless air-integration tanks are available for this dive")

        key = (tank_name or "").strip().lower()
        sensor_info = self.tank_alias_map.get(key)
        if sensor_info is None:
            available = ", ".join(self.available_tanks) or "none"
            raise KeyError(f"Unknown tank '{tank_name}'. Available: {available}")

        sensor_field, display_name = sensor_info
        label = display_name or sensor_field

        rows: List[Tuple[float, float]] = []
        for sample in self.samples:
            time_value = sample.get("time_seconds")
            if not isinstance(time_value, (int, float)):
                continue

            raw_value = sample.get(sensor_field)

            pressure = _normalize_pressure(raw_value)
            if pressure is None:
                continue

            rows.append((float(time_value), pressure))

        if not rows:
            return _pd.DataFrame(columns=[label]).set_index(_pd.Index([], name="time_seconds"))

        df = _pd.DataFrame(rows, columns=["time_seconds", label]).set_index("time_seconds")
        return df


__all__ = ["DiveTimeSeries"]
