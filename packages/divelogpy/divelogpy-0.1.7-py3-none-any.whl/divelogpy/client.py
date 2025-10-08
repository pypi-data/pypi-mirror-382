"""High level API surface for working with Shearwater Cloud exports."""

from __future__ import annotations

import sqlite3
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence

import pandas as pd

from .decoders import (
    decode_metadata_blob,
    decode_petrel_frames,
    decode_petrel_raw_floats,
    decompress_petrel_blob,
)
from .models import (
    Dive,
    DivePayload,
    UnitMeasure,
    build_tank_alias_map,
)
from .pnf_decoder import decode_petrel_v14
from .timeseries import DiveTimeSeries
from .utils import load_json

_SERIAL_TO_NAME = {
    "BADA0606": "Petrel 3",
    "4B5045D8": "Teric",
    "9F33AC3F": "Peregrine",
    "332D752A": "Nerd 2",
}

_MODE_CODE_TO_MODE = {
    0: "ccr",
    1: "oc_rec",
    2: "oc_tec",
    6: "gauge",
}


class DiveLogClient:
    """Context manager providing typed access to the dive log."""

    def __init__(self, database_path: str | Path) -> None:
        self._path = Path(database_path)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            if not self._path.exists():
                raise FileNotFoundError(f"Database not found at {self._path}")
            self._conn = sqlite3.connect(str(self._path))
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DiveLogClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - context protocol
        self.close()

    # ------------------------------------------------------------------

    @staticmethod
    def _coerce_blob(value) -> bytes | None:
        if value is None:
            return None
        if isinstance(value, memoryview):
            return bytes(value)
        if isinstance(value, (bytes, bytearray)):
            return bytes(value)
        if isinstance(value, str):
            return value.encode("utf-8")
        try:
            return bytes(value)
        except TypeError:
            return None

    # ------------------------------------------------------------------

    def get_dives(self) -> Sequence[Dive]:
        """Return raw dive entries (one per computer)."""

        df = self._prepare_dataframe()
        dives: List[Dive] = []
        for _, row in df.iterrows():
            dives.append(self._build_single_dive(row))
        return dives

    def get_primary_computer_dives(self, *, time_window_minutes: int = 2) -> Sequence[Dive]:
        """Return grouped dives aggregated across matching computers."""

        df = self._prepare_dataframe()
        if df.empty:
            return []

        threshold = pd.Timedelta(minutes=time_window_minutes)
        breaks = df["DiveDate"].diff().gt(threshold)
        breaks.iloc[0] = True
        df["group_id"] = breaks.cumsum() - 1

        dives: List[Dive] = []
        for _, group in df.groupby("group_id"):
            dive = self._build_grouped_dive(group)
            dives.append(dive)

        return dives

    # ------------------------------------------------------------------

    def _build_payload(self, row: pd.Series, tank_profile: dict | None = None) -> DivePayload | None:
        blob1 = self._coerce_blob(row.get("data_bytes_1"))
        blob2 = self._coerce_blob(row.get("data_bytes_2"))
        blob3 = self._coerce_blob(row.get("data_bytes_3"))

        if blob1 is None and blob2 is None and blob3 is None:
            return None

        decompressed = decompress_petrel_blob(blob1) if blob1 else None
        floats = decode_petrel_raw_floats(blob1) if blob1 else tuple()
        frames = decode_petrel_frames(blob1) if blob1 else tuple()
        decoded = decode_petrel_v14(decompressed) if decompressed else {}
        samples = decoded.get("samples", [])
        for sample in samples:
            if 'extension' in sample and isinstance(sample['extension'], dict):
                ext = sample['extension']
                for key in ext.keys():
                    sample[key] = ext[key]
                del sample['extension']
        sample_raw = decoded.get("raw_samples", [])
        meta2 = decode_metadata_blob(blob2) if blob2 else {}
        meta3 = decode_metadata_blob(blob3) if blob3 else {}

        tank_entries = None
        if isinstance(tank_profile, dict):
            tank_entries = tank_profile.get("TankData")

        tank_alias_map = None
        tank_display_order = tuple()
        if samples:
            alias_map_raw, display_order = build_tank_alias_map(tank_entries)
            tank_alias_map = alias_map_raw or None
            tank_display_order = display_order

        return DivePayload(
            data_bytes_1=blob1,
            decompressed_bytes_1=decompressed,
            floats_1=floats,
            frames_1=frames,
            samples=tuple(samples),
            sample_records_raw=tuple(sample_raw),
            data_bytes_2=meta2,
            data_bytes_3=meta3,
            timeseries=DiveTimeSeries(
                tuple(samples),
                tuple(sample_raw),
                tank_alias_map,
                tank_display_order,
            )
            if samples
            else None,
        )

    # ------------------------------------------------------------------
    def query(self, sql: str) -> pd.DataFrame:
        """Run a custom SQL query against the database and return a DataFrame."""
        conn = self.connect()
        return pd.read_sql_query(sql, conn)

    def _prepare_dataframe(self) -> pd.DataFrame:
        conn = self.connect()
        query = """
            SELECT
                dd.DiveId,
                dd.DiveDate,
                dd.DiveLengthTime,
                dd.Depth,
                dd.SerialNumber,
                dd.FileName,
                ld.calculated_values_from_samples,
                ld.data_bytes_1,
                ld.data_bytes_2,
                ld.data_bytes_3,
                dd.TankProfileData
            FROM dive_details dd
            LEFT JOIN log_data ld ON dd.DiveId = ld.log_id
            WHERE dd.DiveDate IS NOT NULL
            ORDER BY dd.DiveDate
        """
        df = pd.read_sql_query(query, conn)
        if df.empty:
            return df

        df["DiveDate"] = pd.to_datetime(df["DiveDate"], errors="coerce")
        df["DiveLengthTime"] = pd.to_numeric(df["DiveLengthTime"], errors="coerce")
        df["Depth"] = pd.to_numeric(df["Depth"], errors="coerce")

        calc = df["calculated_values_from_samples"].apply(load_json)
        df["avg_temp"] = pd.to_numeric(calc.apply(lambda d: d.get("AverageTemp")), errors="coerce")
        df["min_temp"] = pd.to_numeric(calc.apply(lambda d: d.get("MinTemp")), errors="coerce")
        df["max_temp"] = pd.to_numeric(calc.apply(lambda d: d.get("MaxTemp")), errors="coerce")

        def _load_metadata(value):
            if isinstance(value, (bytes, bytearray)):
                try:
                    return load_json(value.decode("utf-8"))
                except UnicodeDecodeError:
                    return {}
            return load_json(value)

        meta = df["data_bytes_3"].apply(_load_metadata)
        df["mode_code"] = meta.apply(lambda d:d.get('Mode'))
        df["start_ts"] = pd.to_datetime(meta.apply(lambda d: d.get("StartTime")), unit="s", errors="coerce", utc=True).dt.tz_convert(None)
        df["end_ts"] = pd.to_datetime(meta.apply(lambda d: d.get("EndTime")), unit="s", errors="coerce", utc=True).dt.tz_convert(None)
        df["dive_time_override"] = pd.to_numeric(meta.apply(lambda d: d.get("DiveTimeInSeconds")), errors="coerce")

        df = df.dropna(subset=["DiveDate"]).sort_values("DiveDate").reset_index(drop=True)
        return df
    def get_dive(self, dive_id: str) -> Dive | None:
        """Return a single dive by its unique ID, or None if not found."""
        df = self._prepare_dataframe()
        match = df[df["DiveId"] == dive_id]
        if match.empty:
            return None
        return self._build_single_dive(match.iloc[0])
    def _build_single_dive(self, row: pd.Series) -> Dive:
        start_time = row.get("start_ts")
        if isinstance(start_time, pd.Timestamp) and pd.isna(start_time):
            start_time = None
        end_time = row.get("end_ts")
        if isinstance(end_time, pd.Timestamp) and pd.isna(end_time):
            end_time = None

        duration_seconds = None
        if start_time is not None and end_time is not None:
            duration_seconds = (end_time - start_time).total_seconds()
        else:
            duration_seconds = row.get("dive_time_override")
            if pd.isna(duration_seconds):
                duration_seconds = row.get("DiveLengthTime")
            if pd.isna(duration_seconds):
                duration_seconds = None
            elif duration_seconds is not None:
                duration_seconds = float(duration_seconds)

        name = self._extract_computer_name(row.get("FileName"), row.get("SerialNumber"))
        
        mode_code = row.get("mode_code")
        dive_mode = _MODE_CODE_TO_MODE.get(mode_code, "unknown")

        temp_measure = UnitMeasure(float(row["avg_temp"]) if pd.notna(row.get("avg_temp")) else None, "F")
        max_depth = float(row["Depth"]) if pd.notna(row.get("Depth")) else None



        start_value: datetime | None
        if isinstance(start_time, pd.Timestamp):
            start_value = start_time.to_pydatetime()
        else:
            start_value = start_time

        end_value: datetime | None
        if isinstance(end_time, pd.Timestamp):
            end_value = end_time.to_pydatetime()
        else:
            end_value = end_time

        tank_profile = load_json(row.get("TankProfileData"))
        payload = self._build_payload(row, tank_profile)
        tank_entries = tuple(tank_profile.get("TankData") or []) if isinstance(tank_profile, dict) else tuple()
        tank_data = tuple(
            entry
            for entry in tank_entries
            if (entry.get("DiveTransmitter") or {}).get("IsOn")
        )
        gas_profiles = tuple(tank_profile.get("GasProfiles") or []) if isinstance(tank_profile, dict) else tuple()

        return Dive(
            dive_id=str(row["DiveId"]),
            start=start_value,
            end=end_value,
            duration_seconds=duration_seconds,
            mode=dive_mode,
            temp=temp_measure,
            max_depth=max_depth,
            computer_names=[name],
            computer_name=name,
            payload=payload,
            primary_computer=None,
            controller=None,
            monitor=None,
            secondary_computer=None,
            gas_profiles=gas_profiles,
            tank_data=tank_data,
            linked_dives=tuple(),
        )

    def _build_grouped_dive(self, group: pd.DataFrame) -> Dive:
        start_candidates = group["start_ts"].dropna()
        start_time = start_candidates.min() if not start_candidates.empty else group["DiveDate"].min()
        if isinstance(start_time, pd.Timestamp) and pd.isna(start_time):
            start_time = None

        end_candidates = group["end_ts"].dropna()
        end_time = end_candidates.max() if not end_candidates.empty else None
        if isinstance(end_time, pd.Timestamp) and pd.isna(end_time):
            end_time = None

        duration_candidates = group["dive_time_override"].dropna()
        fallback_duration = duration_candidates.max() if not duration_candidates.empty else group["DiveLengthTime"].dropna().max()
        if end_time is None and start_time is not None and pd.notna(fallback_duration):
            end_time = start_time + pd.to_timedelta(fallback_duration, unit="s")

        total_seconds = None
        if start_time is not None and end_time is not None:
            total_seconds = (end_time - start_time).total_seconds()
        elif pd.notna(fallback_duration):
            total_seconds = float(fallback_duration)

        component_records: List[tuple[Dive, pd.Series]] = []
        for _, row in group.iterrows():
            component_records.append((self._build_single_dive(row), row))

        if not component_records:
            raise ValueError("Unable to build grouped dive")

        ccr_present = any(row.get("mode_code") == 0 for _, row in component_records)

        priority_map = {
            "cc_primary": 0,
            "cc_monitor": 1,
            "cc_secondary": 2,
            "oc_primary": 3,
            "gauge": 4,
        }

        dedup: "OrderedDict[str, tuple[str, int, Dive, pd.Series]]" = OrderedDict()
        for component, row in component_records:
            label = component.display_name()
            role = self._determine_role(
                label,
                row.get("SerialNumber"),
                row.get("mode_code"),
                ccr_present=ccr_present,
            )
            priority = priority_map.get(role, 5)
            if label not in dedup or priority < dedup[label][1]:
                dedup[label] = (role, priority, component, row)

        ordered = sorted(dedup.items(), key=lambda item: (item[1][1], item[0]))
        if not ordered:
            raise ValueError("Unable to determine computers for dive group")

        computer_names = [component.display_name() for component, _ in component_records]
        component_modes = [component.mode for component, _ in component_records]

        if any(mode == "ccr" for mode in component_modes):
            dive_mode = "ccr"
        elif component_modes:
            dive_mode = component_modes[0]
        else:
            dive_mode = "unknown"

        primary_dive: Dive | None = None
        controller_dive: Dive | None = None
        monitor_dive: Dive | None = None
        secondary_dive: Dive | None = None

        for _, (role, _, component, _) in ordered:
            if role == "cc_primary" and controller_dive is None:
                controller_dive = primary_dive = component
            elif role == "cc_monitor" and monitor_dive is None:
                monitor_dive = component
            elif role == "cc_secondary" and secondary_dive is None:
                secondary_dive = component
            elif role == "oc_primary" and primary_dive is None:
                primary_dive = component
            elif role == "gauge" and secondary_dive is None:
                secondary_dive = component

        if primary_dive is None:
            primary_dive = ordered[0][1][2]

        temp_values = group["avg_temp"].dropna()
        water_temp = float(temp_values.mean()) if not temp_values.empty else None
        temp_measure = UnitMeasure(water_temp, "F")

        max_depth = group["Depth"].dropna().max()

        start_value: datetime | None
        if isinstance(start_time, pd.Timestamp):
            start_value = start_time.to_pydatetime()
        else:
            start_value = start_time

        end_value: datetime | None
        if isinstance(end_time, pd.Timestamp):
            end_value = end_time.to_pydatetime()
        else:
            end_value = end_time

        combined_tanks: List[Dict[str, Any]] = []
        seen_tanks: set[tuple[Any, Any]] = set()
        combined_profiles: List[Dict[str, Any]] = []
        for component, _ in component_records:
            for entry in component.tank_data:
                transmitter = entry.get("DiveTransmitter") or {}
                key = (
                    transmitter.get("TankIndex"),
                    transmitter.get("UnformattedSerialNumber"),
                )
                if key not in seen_tanks:
                    combined_tanks.append(entry)
                    seen_tanks.add(key)
            combined_profiles.extend(component.gas_profiles)

        payload = primary_dive.payload if primary_dive else None

        return Dive(
            dive_id=str(ordered[0][1][3]["DiveId"]),
            start=start_value,
            computer_name=primary_dive.computer_name,
            end=end_value,
            duration_seconds=total_seconds,
            mode=dive_mode,
            temp=temp_measure,
            max_depth=float(max_depth) if pd.notna(max_depth) else None,
            computer_names=list(dict.fromkeys(computer_names)),
            payload=payload,
            primary_computer=primary_dive,
            controller=controller_dive,
            monitor=monitor_dive,
            secondary_computer=secondary_dive,
            gas_profiles=tuple(combined_profiles),
            tank_data=tuple(combined_tanks),
            linked_dives=tuple(component for component, _ in component_records),
        )

    @staticmethod
    def _extract_computer_name(filename: str | None, serial: str | None) -> str:
        serial_str = str(serial).upper() if serial is not None else ""
        if isinstance(filename, str) and "[" in filename:
            return filename.split("[", 1)[0].strip()
        if serial_str in _SERIAL_TO_NAME:
            return _SERIAL_TO_NAME[serial_str]
        if isinstance(serial, str) and serial.strip():
            return serial.strip()
        return "Unknown Computer"

    @staticmethod
    def _is_cc_primary_candidate(name: str, serial: str | None) -> bool:
        serial_str = str(serial).upper() if serial is not None else ""
        label = (name or serial_str).upper()
        return "PETREL" in label or serial_str == "BADA0606"

    @staticmethod
    def _determine_role(name: str, serial: str | None, mode_code: int | None, *, ccr_present: bool) -> str:
        serial_str = str(serial).upper() if serial is not None else ""
        label = (name or serial_str).upper()

        if mode_code == 6:
            return "gauge"

        if "NERD" in label:
            return "cc_monitor" if ccr_present else "oc_primary"

        if "PETREL" in label or serial_str == "BADA0606":
            return "cc_primary"

        if "TERIC" in label or serial_str == "4B5045D8":
            return "cc_secondary" if ccr_present else "oc_primary"

        if "PEREGRINE" in label or serial_str == "9F33AC3F":
            return "oc_primary"

        return "oc_primary"


def get_client(database_path: str | Path) -> DiveLogClient:
    """Convenience constructor used by notebook examples."""

    return DiveLogClient(database_path)
