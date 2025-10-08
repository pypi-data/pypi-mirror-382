"""Domain models used by the dive log client."""

from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
import math
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from .timeseries import DiveTimeSeries


class UnitMeasure:
    """Wrap a numeric value with unit conversion helpers."""

    _CONVERSIONS = {
        ("F", "C"): lambda value: (value - 32.0) * 5.0 / 9.0,
        ("C", "F"): lambda value: value * 9.0 / 5.0 + 32.0,
    }

    def __init__(self, value: float | None, unit: str) -> None:
        self._value = value
        self._unit = unit.upper() if unit else unit

    @property
    def value(self) -> float | None:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def available_units(self) -> Sequence[str]:
        units = set()
        if self._unit:
            units.add(self._unit)
        for base, target in self._CONVERSIONS:
            units.add(base)
            units.add(target)
        return sorted(u for u in units if u)

    def as_unit(self, target_unit: str) -> float | None:
        """Return the value converted to *target_unit* (if possible)."""
        if self._value is None:
            return None
        target = target_unit.upper()
        if target == self._unit:
            return self._value
        key = (self._unit, target)
        if key not in self._CONVERSIONS:
            raise ValueError(f"Unsupported conversion {self._unit} -> {target}")
        return self._CONVERSIONS[key](self._value)

    def convert(self, target_unit: str) -> "UnitMeasure":
        """Return a new :class:`UnitMeasure` in the requested unit."""
        return UnitMeasure(self.as_unit(target_unit), target_unit)

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        return f"UnitMeasure(value={self._value!r}, unit='{self._unit}')"



class Sensor:
    """PO₂ sensor samples for a single sensor."""

    sensor_index: int
    calibration_ppo2: float | None
    timeseries: pd.DataFrame
    calibration_mv: float | None = None
    milivolts: pd.Series
    ppo2: pd.Series

    def __init__(self, sensor_index: int, timeseries: pd.DataFrame, calibration_ppo2: float | None = None, calibration_mv: float | None = None):
        self.sensor_index = sensor_index
        self.timeseries = timeseries
        self.calibration_ppo2 = calibration_ppo2 or 0.99
        self.calibration_mv = calibration_mv or self.timeseries.reset_index().set_index('average_ppo2').loc[self.calibration_ppo2][f'sensor{self.sensor_index}_millivolts'].mean() if not self.timeseries.empty else None
        self.milivolts = self.timeseries[f'sensor{self.sensor_index}_millivolts'] if f'sensor{self.sensor_index}_millivolts' in self.timeseries else pd.Series(dtype=float)
        self.ppo2 = (self.milivolts / self.calibration_mv * self.calibration_ppo2) if self.calibration_mv else pd.Series(dtype=float)

    def to_df(self, include_depth=False):  # pragma: no cover - convenience alias   
        fields = [f'sensor{self.sensor_index}_millivolts']
        if include_depth and 'depth_ft' in self.timeseries:
            fields.insert(0,'depth_ft')
        return self.timeseries[fields]

    def plot(self):
        from .plotting import plot_timeseries
        return plot_timeseries(self.timeseries, scale_groups=[[f'sensor{self.sensor_index}_millivolts']])

    def to_process(self,include_depth=False,filter_low_setpoint=False)-> pd.DataFrame:
        fields = [f'sensor{self.sensor_index}_millivolts']
        df = self.timeseries.copy()
        if include_depth and 'depth_ft' in df:
            fields.insert(0,'depth_ft')
            df = df.where(df['depth_ft']!=np.inf).where(df['depth_ft']>0).dropna(subset=['depth_ft'])
        if filter_low_setpoint:
            df = df[df[f'ppo2_setpoint']==df[f'ppo2_setpoint'].max()]
        df_chgs = np.log(df[fields]) - np.log(df[fields].shift(1)).dropna()
        df_chgs = df_chgs.iloc[1:]
        return df_chgs
    def extract_residuals(self, independent_vars=['depth_ft'],filter_low_setpoint=False)-> pd.DataFrame:
        import pandas as pd
        import statsmodels.api as sm
        df = self.to_process(include_depth=True,filter_low_setpoint=filter_low_setpoint)
        df = df.copy()
        df.index.name = "time_seconds"
        sensor_col = f'sensor{self.sensor_index}_millivolts'
        residuals = pd.DataFrame(index=df.index)
        X = sm.add_constant(df[independent_vars])
        y = df[sensor_col]
        model = sm.OLS(y, X).fit()
        residuals[sensor_col] = model.resid
        residuals[independent_vars] = df[independent_vars]
        return residuals



class SensorCollection(Sequence[Sensor]):
    """Thin wrapper that offers helpers across all sensor series."""

    def __init__(self, series: Iterable[Sensor]):
        self._series: List[Sensor] = list(series)

    def __getitem__(self, index):
        return self._series[index]

    def __len__(self) -> int:
        return len(self._series)

    def __iter__(self) -> Iterator[Sensor]:  # pragma: no cover - trivial
        return iter(self._series)

    def to_df(self):  # pragma: no cover - convenience only
        return pd.concat([sensor.timeseries[[f'sensor{sensor.sensor_index}_millivolts']] for sensor in self._series], axis=1).assign(depth_ft=self._series[0].timeseries['depth_ft'])
    def plot(self):
        from .plotting import plot_timeseries
        return plot_timeseries(self.to_df(), scale_groups=[[f'sensor{sensor_index}_millivolts' for sensor_index in range(1,len(self)+1)]])
    def plot_po2_millivolts_scatter(self):
        from .plotting import plot_po2_millivolts_scatter
        # return plot_po2_millivolts_scatter(self.to_df().assign(average_ppo2=self._series[0].timeseries['average_ppo2'] if 'average_ppo2' in self._series[0].timeseries else np.nan))
        return plot_po2_millivolts_scatter(self.to_df().assign(average_ppo2=pd.DataFrame([i.ppo2 for i in self._series]).mean(axis=0) if self._series else np.nan))
    def to_process(self,include_depth=False,filter_low_setpoint=False)-> pd.DataFrame:
        df = pd.concat([sensor.to_process(include_depth=include_depth,filter_low_setpoint=filter_low_setpoint) for sensor in self._series], axis=1)
        if include_depth:
            df = df.loc[:,~df.columns.duplicated()]
        return df
    def extract_residuals(self, independent_vars=['depth_ft'],filter_low_setpoint=False)-> pd.DataFrame:
        import pandas as pd
        import statsmodels.api as sm
        df = self.to_process(include_depth=True,filter_low_setpoint=filter_low_setpoint)
        df = df.copy()
        if 'depth_ft' in df.columns:
            if df.at[df.index[0],'depth_ft'] == np.inf:
                df = df.iloc[1:]
        df.index.name = "time_seconds"
        sensor_cols = [f'sensor{sensor.sensor_index}_millivolts' for sensor in self._series]
        residuals = pd.DataFrame(index=df.index)
        X = sm.add_constant(df[independent_vars])
        for s in sensor_cols:
            y = df[s]
            model = sm.OLS(y, X).fit()
            residuals[s] = model.resid
        residuals[independent_vars] = df[independent_vars]
        return residuals
    

    def remove_first_principal_component(self, use_depth_residuals=True,remove_autocorrelations=True,filter_low_setpoint=False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        
        """
        import numpy as np
        import pandas as pd
        from sklearn.decomposition import PCA
        df: pd.DataFrame = pd.DataFrame()
        if use_depth_residuals:
            df = self.extract_residuals(independent_vars=['depth_ft'],filter_low_setpoint=filter_low_setpoint)
        else:
            df = self.to_process()
        df = df.copy()
        cols = df.columns
        X = df[cols].astype(float).dropna()
        X_std = (X - X.mean()) / X.std(ddof=1)
        pca = PCA()
        Z = pca.fit_transform(X_std)

        pc1 = Z[:, 0]

        # 2) Per-sensor regression on pc1 -> fitted shared + residual (sensor units)
        A = np.c_[np.ones(len(X)), pc1]
        F = pd.DataFrame(index=X.index, columns=cols, dtype=float)   # fitted (shared)
        R = pd.DataFrame(index=X.index, columns=cols, dtype=float)   # residuals (sensor noise, in original units)

        noise_var = {}
        total_var = {}
        noise_fraction = {}
        r2 = {}

        for c in [cx for cx in cols if cx not in ['depth_ft']]:
            y = X[c].values
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)
            yhat = A @ beta
            resid = y - yhat

            F[c] = yhat
            R[c] = resid

            # TSS/RSS using unbiased variances (ddof=1); factors cancel in the ratio
            v_total = np.var(y, ddof=1)
            v_noise = np.var(resid, ddof=1)

            total_var[c] = v_total
            noise_var[c] = v_noise
            noise_fraction[c] = v_noise / v_total            # == 1 - R^2
            r2[c] = 1.0 - noise_fraction[c]

        summary = pd.DataFrame({
            "total_var": pd.Series(total_var),
            "noise_var": pd.Series(noise_var),
            "noise_fraction": pd.Series(noise_fraction),
            "R2_vs_PC1": pd.Series(r2)
        })
        R = R.drop(columns=['depth_ft'], errors='ignore')
        if remove_autocorrelations:
            def ar1_innovations(s: pd.Series) -> pd.Series:
                y = s.dropna().astype(float)
                if len(y) < 5:
                    return y * np.nan  # not enough data
                y0, y1 = y.shift(1).dropna().align(y.dropna(), join="inner")
                # OLS phi1 = cov/var = corr * (std_y/std_y) -> here simpler as:
                phi1 = np.cov(y1, y0, bias=False)[0,1] / np.var(y0, ddof=1)
                e = y - phi1 * y.shift(1)
                return e.dropna().rename(f"{s.name}")

            innov_df = pd.concat([ar1_innovations(R[c]) for c in R.columns], axis=1)
            return innov_df, summary
        
        return R, summary


    def plot_sensor_noise(self,filter_low_setpoint=False):
        from .plotting import plot_sensor_strip
        return plot_sensor_strip(df=self.remove_first_principal_component(use_depth_residuals=True,remove_autocorrelations=True,filter_low_setpoint=filter_low_setpoint)[0])

    def plot_noise_share(self,filter_low_setpoint=False):
        from .plotting import plot_noise_share
        return plot_noise_share(self.remove_first_principal_component(use_depth_residuals=True,remove_autocorrelations=True,filter_low_setpoint=filter_low_setpoint)[1])


@dataclass(frozen=True)
class AirIntegrationSeries:
    """Metadata and samples for a wireless air-integration transmitter."""

    name: str
    tank_index: int | None
    start_pressure_psi: float | None
    end_pressure_psi: float | None
    samples: Tuple[Tuple[float, float], ...] = field(default_factory=tuple)
    default_script_term: str | None = None
    transmitter_serial: str | None = None
    is_enabled: bool | None = None
    gas_profile: Mapping[str, Any] | None = None
    sensor_field: str | None = None

    @property
    def pressure_drop_psi(self) -> float | None:
        if self.start_pressure_psi is None or self.end_pressure_psi is None:
            return None
        return self.start_pressure_psi - self.end_pressure_psi

    @property
    def sample_count(self) -> int:
        return len(self.samples)

    @property
    def start_time_seconds(self) -> float | None:
        return self.samples[0][0] if self.samples else None

    @property
    def end_time_seconds(self) -> float | None:
        return self.samples[-1][0] if self.samples else None

    def to_dataframe(self):  # pragma: no cover - convenience helper
        import pandas as pd

        if not self.samples:
            return pd.DataFrame(columns=["seconds", "pressure_psi"])
        return pd.DataFrame(self.samples, columns=["seconds", "pressure_psi"]).set_index("seconds")


@dataclass(frozen=True)
class DivePayload:
    """Container for raw computer payloads and decoded helpers."""

    data_bytes_1: bytes | None = None
    decompressed_bytes_1: bytes | None = None
    floats_1: Sequence[float] = field(default_factory=tuple)
    frames_1: Sequence[Tuple[float, ...]] = field(default_factory=tuple)
    samples: Sequence[Dict[str, Any]] = field(default_factory=tuple)
    sample_records_raw: Sequence[bytes] = field(default_factory=tuple)
    data_bytes_2: Dict[str, Any] = field(default_factory=dict)
    data_bytes_3: Dict[str, Any] = field(default_factory=dict)
    timeseries: "DiveTimeSeries" | None = None


@dataclass(frozen=True)
class Dive:
    """A dive event aggregated across matching computers."""

    dive_id: str
    computer_name: str
    start: datetime | None
    end: datetime | None
    duration_seconds: float | None
    mode: str
    temp: UnitMeasure
    max_depth: float | None
    computer_names: Sequence[str]
    payload: DivePayload | None = None
    primary_computer: "Dive" | None = None
    controller: "Dive" | None = None
    monitor: "Dive" | None = None
    secondary_computer: "Dive" | None = None
    gas_profiles: Sequence[Dict[str, Any]] = field(default_factory=tuple)
    tank_data: Sequence[Dict[str, Any]] = field(default_factory=tuple)
    linked_dives: Tuple["Dive", ...] = field(default_factory=tuple)

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        primary = self._link_label(self.primary_computer)
        return (
            "Dive("
            f"id={self.dive_id!r}, mode={self.mode!r}, start={self.start}, duration_seconds={self.duration_seconds}, "
            f"primary={primary!r}, computers={list(self.computer_names)}"
            ")"
        )

    def display_name(self) -> str:
        """Return a friendly label for the dive's computer."""

        return self.computer_name 

    @property
    def timeseries(self) -> "DiveTimeSeries | None":
        if self.payload:
            return self.payload.timeseries
        return None
    
    @property
    def sensors(self) -> SensorCollection:
        sensors = []
        if self.timeseries:
            for sensor_index in range(1,4):
                series = self.timeseries.to_df()
                sensors.append(Sensor(sensor_index=sensor_index, timeseries=series))
            return SensorCollection(sensors)
        return SensorCollection([])

    @property
    def air_integration(self) -> Tuple[AirIntegrationSeries, ...]:
        if not self.tank_data:
            return tuple()
        samples = self.payload.samples if (self.payload and self.payload.samples) else ()
        return _build_air_integration_entries(self.tank_data, samples)

    @staticmethod
    def _link_label(link: "Dive" | None) -> str | None:
        if isinstance(link, Dive):
            return link.display_name()
        if isinstance(link, str):  # backwards compatibility
            return link
        return None

    @property
    def primary_label(self) -> str | None:
        return self._link_label(self.primary_computer)

    @property
    def primary_computer_name(self) -> str | None:
        return self.primary_label

    @property
    def controller_label(self) -> str | None:
        return self._link_label(self.controller)

    @property
    def controller_name(self) -> str | None:
        return self.controller_label

    @property
    def monitor_label(self) -> str | None:
        return self._link_label(self.monitor)

    @property
    def monitor_name(self) -> str | None:
        return self.monitor_label

    @property
    def secondary_label(self) -> str | None:
        return self._link_label(self.secondary_computer)

    @property
    def secondary_computer_name(self) -> str | None:
        return self.secondary_label


_TANK_INDEX_CANDIDATE_FIELDS: Dict[int, Tuple[str, ...]] = {
    0: ("wai_sensor0_pressure",),
    1: ("wai_sensor1_pressure",),
    2: ("wai_sensor2_pressure",),
    3: ("wai_sensor3_pressure",),
}

_SENTINEL_PRESSURES = {0, 65535, 65534}

_PRESSURE_FIELD_SCALE: Dict[str, float] = {
    "wai_sensor0_pressure": 2.0,
    "wai_sensor1_pressure": 2.0,
    "wai_sensor2_pressure": 2.0,
    "wai_sensor3_pressure": 2.0,
}


def _select_first_available_field(
    samples: Sequence[Dict[str, Any]] | None,
    candidates: Sequence[str],
) -> str | None:
    if not candidates:
        return None
    if not samples:
        return candidates[0]

    for field in candidates:
        for sample in samples:
            value = _retrieve_sample_value(sample, field)
            if value not in (None, 0, 65535, 65534):
                return field
    return candidates[0]


def _build_air_integration_entries(
    tank_entries: Sequence[Dict[str, Any]],
    samples: Sequence[Dict[str, Any]] | None,
) -> Tuple[AirIntegrationSeries, ...]:
    selected = _select_tank_entries(tank_entries)
    if not selected:
        return tuple()

    sample_series_cache: Dict[str, Tuple[Tuple[float, float], ...]] = {}
    results: List[AirIntegrationSeries] = []

    for entry in selected:
        transmitter = entry.get("DiveTransmitter") or {}
        tank_index = transmitter.get("TankIndex")
        candidates = _TANK_INDEX_CANDIDATE_FIELDS.get(tank_index, tuple())
        sensor_field = _select_first_available_field(samples, candidates)
        if sensor_field is None:
            continue
        if sensor_field not in sample_series_cache:
            sample_series_cache[sensor_field] = _extract_pressure_series(samples, sensor_field)
        series = sample_series_cache[sensor_field]

        results.append(
            AirIntegrationSeries(
                name=_resolve_transmitter_name(transmitter, tank_index),
                tank_index=tank_index,
                start_pressure_psi=_coerce_pressure(entry.get("StartPressurePSI")),
                end_pressure_psi=_coerce_pressure(entry.get("EndPressurePSI")),
                samples=series,
                default_script_term=transmitter.get("DefaultScriptTerm"),
                transmitter_serial=transmitter.get("UnformattedSerialNumber"),
                is_enabled=transmitter.get("IsOn"),
                gas_profile=entry.get("GasProfile"),
                sensor_field=sensor_field,
            )
        )

    results.sort(key=lambda item: (item.tank_index if item.tank_index is not None else 99))
    return tuple(results)


def _select_tank_entries(tank_entries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best: Dict[Any, Dict[str, Any]] = {}
    for entry in tank_entries or []:
        transmitter = entry.get("DiveTransmitter") or {}
        if not transmitter.get("IsOn"):
            continue
        key = transmitter.get("TankIndex")
        if key is None:
            script_term = transmitter.get("DefaultScriptTerm")
            if not script_term:
                continue
            key = script_term

        current = best.get(key)
        if current is None or _entry_score(entry) > _entry_score(current):
            best[key] = entry

    ordered_keys = sorted(best.keys(), key=lambda value: value if isinstance(value, int) else 99)
    return [best[key] for key in ordered_keys]


def _entry_score(entry: Dict[str, Any]) -> Tuple[int, int, int]:
    transmitter = entry.get("DiveTransmitter") or {}
    is_on = 1 if transmitter.get("IsOn") else 0
    start = 1 if _coerce_pressure(entry.get("StartPressurePSI")) is not None else 0
    end = 1 if _coerce_pressure(entry.get("EndPressurePSI")) is not None else 0
    return (is_on, start, end)


def _resolve_transmitter_name(transmitter: Dict[str, Any], tank_index: int | None) -> str:
    name = transmitter.get("Name") if isinstance(transmitter, dict) else None
    if isinstance(name, str):
        cleaned = name.replace("\x00", "").strip()
        if cleaned:
            return cleaned
    if tank_index is not None:
        return f"Tank {tank_index + 1}"
    term = transmitter.get("DefaultScriptTerm") if isinstance(transmitter, dict) else None
    if isinstance(term, str) and term:
        return term.rsplit("/", 1)[-1]
    return "Unknown Tank"


def _coerce_pressure(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        if value in _SENTINEL_PRESSURES:
            return None
        return float(value)
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
        return numeric
    return None


def _extract_pressure_series(
    samples: Sequence[Dict[str, Any]] | None,
    field: str,
) -> Tuple[Tuple[float, float], ...]:
    if not samples:
        return tuple()

    series: List[Tuple[float, float]] = []
    for sample in samples:
        raw_value = _retrieve_sample_value(sample, field)
        pressure = _coerce_pressure(raw_value)
        if pressure is not None:
            pressure *= _PRESSURE_FIELD_SCALE.get(field, 1.0)
        if pressure is None:
            continue
        time_value = sample.get("time_seconds")
        if isinstance(time_value, (int, float)):
            series.append((float(time_value), pressure))

    return tuple(series)


def _retrieve_sample_value(sample: Dict[str, Any], field: str) -> Any:
    return sample.get(field)


def build_tank_alias_map(
    tank_entries: Sequence[Dict[str, Any]] | None,
) -> Tuple[Dict[str, Tuple[str, str]], Tuple[Tuple[str, str], ...]]:
    """Return alias lookups for active wireless transmitters."""

    alias_map: Dict[str, Tuple[str, str]] = {}
    display_order: List[Tuple[str, str]] = []
    seen_fields: set[str] = set()

    for entry in tank_entries or []:
        transmitter = entry.get("DiveTransmitter") or {}
        if not transmitter.get("IsOn"):
            continue

        index = transmitter.get("TankIndex")
        sensor_field = _select_first_available_field(None, _TANK_INDEX_CANDIDATE_FIELDS.get(index, tuple()))
        if sensor_field is None:
            continue

        display_name = _resolve_transmitter_name(transmitter, index)
        if sensor_field not in seen_fields:
            display_order.append((display_name, sensor_field))
            seen_fields.add(sensor_field)

        for alias in _iter_tank_aliases(transmitter, index, display_name):
            normalized = alias.strip().lower()
            if normalized:
                alias_map[normalized] = (sensor_field, display_name)

    return alias_map, tuple(display_order)


def _iter_tank_aliases(transmitter: Dict[str, Any], index: int | None, display_name: str) -> Iterable[str]:
    aliases = set()

    if isinstance(display_name, str) and display_name:
        aliases.add(display_name)

    name = transmitter.get("Name") if isinstance(transmitter, dict) else None
    if isinstance(name, str):
        aliases.add(name.replace("\x00", ""))

    if index is not None:
        aliases.add(f"tank{index + 1}")
        aliases.add(f"tank_{index + 1}")

    script_term = transmitter.get("DefaultScriptTerm")
    if isinstance(script_term, str) and script_term:
        aliases.add(script_term)
        aliases.add(script_term.rsplit("/", 1)[-1])

    serial = transmitter.get("UnformattedSerialNumber")
    if serial is not None:
        aliases.add(str(serial))

    return aliases
