"""Core helpers for wireless air-integration analytics."""

from __future__ import annotations

from typing import Iterable, List, Sequence

import pandas as pd

from .client import DiveLogClient
from .models import AirIntegrationSeries, Dive


def _dive_label(dive: Dive | None) -> str | None:
    if isinstance(dive, Dive):
        return dive.display_name()
    if isinstance(dive, str):  # backwards compatibility
        return dive
    return None


def _choose_entry(entries: Sequence[AirIntegrationSeries]) -> AirIntegrationSeries | None:
    candidates = [
        entry
        for entry in entries
        if entry.is_enabled and (
            entry.sample_count
            or entry.start_pressure_psi is not None
            or entry.end_pressure_psi is not None
        )
    ]
    if not candidates:
        return None

    def score(entry: AirIntegrationSeries) -> tuple[int, int, int, int]:
        return (
            entry.sample_count,
            int(entry.start_pressure_psi is not None) + int(entry.end_pressure_psi is not None),
            1 if entry.is_enabled else 0,
            -1 if entry.tank_index is None else -entry.tank_index,
        )

    return max(candidates, key=score)


def oc_air_integration_table(client: DiveLogClient, *, dives: Sequence[Dive] | None = None) -> pd.DataFrame:
    """Return a table of open-circuit dives with air-integration pressure data."""

    source_dives: Iterable[Dive] = dives if dives is not None else client.get_primary_computer_dives()

    rows: List[dict] = []
    for dive in source_dives:
        mode = dive.mode or ""
        if not mode.startswith("oc"):
            continue
        entry = _choose_entry(dive.air_integration)
        if entry is None:
            continue

        rows.append(
            {
                "dive_id": dive.dive_id,
                "start": dive.start,
                "end": dive.end,
                "primary_computer": _dive_label(dive.primary_computer),
                "ai_sensor": entry.name,
                "sensor_field": entry.sensor_field,
                "start_pressure_psi": entry.start_pressure_psi,
                "end_pressure_psi": entry.end_pressure_psi,
                "pressure_drop_psi": entry.pressure_drop_psi,
                "pressure_samples": entry.sample_count,
                "start_pressure_time_s": entry.start_time_seconds,
                "end_pressure_time_s": entry.end_time_seconds,
            }
        )

    columns = [
        "dive_id",
        "start",
        "end",
        "primary_computer",
        "ai_sensor",
        "sensor_field",
        "start_pressure_psi",
        "end_pressure_psi",
        "pressure_drop_psi",
        "pressure_samples",
        "start_pressure_time_s",
        "end_pressure_time_s",
    ]

    if not rows:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame.from_records(rows).sort_values("start", ascending=False).reset_index(drop=True)


__all__ = ["oc_air_integration_table"]
