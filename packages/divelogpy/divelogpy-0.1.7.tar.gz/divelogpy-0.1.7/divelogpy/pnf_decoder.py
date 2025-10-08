"""Decode Petrel native log data (PNF v14) into structured records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from .pnf_constants import PNF_V14_CONSTANTS as C

_RECORD_SIZE = C["PNF_RECORD_SIZE"]
_SAMPLE_TYPE = C["LOG_RECORD_TYPE_DIVE_SAMPLE"]
_SAMPLE_EXT_TYPE = C.get("LOG_RECORD_TYPE_DIVE_SAMPLE_EXT")


@dataclass
class DiveSample:
    index: int
    raw: bytes
    values: Dict[str, Any]


def _u16_be(record: bytes, offset: int) -> int:
    if offset + 1 >= len(record):
        return 0
    return (record[offset] << 8) | record[offset + 1]


def _u8(record: bytes, offset: int) -> int:
    if offset >= len(record):
        return 0
    return record[offset]


def decode_samples(data: bytes) -> List[DiveSample]:
    """Return decoded dive samples for a v14 Petrel payload."""

    records = [data[i : i + _RECORD_SIZE] for i in range(0, len(data), _RECORD_SIZE) if len(data[i : i + _RECORD_SIZE]) == _RECORD_SIZE]

    samples: List[DiveSample] = []
    last_sample: DiveSample | None = None

    time_increment = C.get("RECORD_TIME_INCREMENT", 10)

    logical_index = 0
    for record in records:
        record_type = record[0]
        if record_type == _SAMPLE_TYPE:
            depth_raw = _u16_be(record, C["DEPTH_1ST_BYTE_OFFSET"])
            next_stop_raw = _u16_be(record, C["NEXTSTOPDEPTH_1ST_BYTE_OFFSET"])
            time_to_surface_raw = _u16_be(record, C["TIMETOSURFACE_1ST_BYTE_OFFSET"])
            avg_ppo2_raw = _u8(record, C["AVERAGEPPO2_OFFSET"])
            temp_f_raw = _u8(record, C["WATERTEMPERATURE_OFFSET"])
            battery_voltage_raw = _u16_be(record, C["BATTERYVOLTAGE_OFFSET_MSB"])
            setpoint_raw = _u8(record, C["CURRENTPPO2SETPOINT_OFFSET"])
            wai_s1 = _u16_be(record, C["WAI_SENSOR_1_1ST_BYTE_OFFSET"])
            wai_s0 = _u16_be(record, C["WAI_SENSOR_0_1ST_BYTE_OFFSET"])
            wai_time = _u8(record, C["WAI_GAS_TIME_REMAIN_SENSOR_OFFSET"])
            at_plus_five_raw = _u16_be(record, C["ATPLUSFIVE_1ST_BYTE_OFFSET"])
            rmv_raw = _u16_be(record, C["RESPIRATORY_MINUTE_VOLUME_1ST_BYTE_OFFSET"])

            water_temp_c = None
            if temp_f_raw not in (0, 255):
                water_temp_c = round((temp_f_raw - 32) * 5.0 / 9.0, 2)

            sample = DiveSample(
                index=len(samples),
                raw=record,
                values={
                    "time_seconds": logical_index * time_increment,
                    "record_type": record_type,
                    "depth_raw": depth_raw,
                    "depth_ft": depth_raw / 10.0,
                    "depth_m": round(depth_raw / 10.0 * 0.3048, 4),
                    "next_stop_depth_ft": next_stop_raw / 10.0,
                    "time_to_surface_raw": time_to_surface_raw,
                    "average_ppo2": avg_ppo2_raw / 100.0,
                    "gas_o2_percent": _u8(record, C["CURRENTGASO2PERCENT_OFFSET"]),
                    "gas_he_percent": _u8(record, C["CURRENTGASHEPERCENT_OFFSET"]),
                    "no_deco_limit_minutes": _u8(record, C["CURRENTNODECOLIMIT_OFFSET"]),
                    "battery_percent_remaining": _u8(record, C["BATTERY_PERCENT_REMAINING_OFFSET"]),
                    "gas_index": _u8(record, C["GAS_OFFSET"]),
                    "sensor1_millivolts": _u8(record, C["SENSOR1MILLIVOLTS_OFFSET"]),
                    "sensor2_millivolts": _u8(record, C["SENSOR2MILLIVOLTS_OFFSET"]),
                    "sensor3_millivolts": _u8(record, C["SENSOR3MILLIVOLTS_OFFSET"]),
                    "water_temp_f": temp_f_raw,
                    "water_temp_c": water_temp_c,
                    "battery_voltage_raw": battery_voltage_raw,
                    "battery_voltage_v": battery_voltage_raw / 10.0,
                    "ppo2_setpoint": setpoint_raw / 100.0,
                    "wai_sensor1_pressure": wai_s1,
                    "wai_sensor0_pressure": wai_s0,
                    "wai_time_remaining_min": None if wai_time in (0, 255) else wai_time,
                    "cns_percent": _u8(record, C["CENTRALNERVOUSSYSTEMPERCENTAGE_OFFSET"]),
                    "deco_ceiling_ft": _u8(record, C["DECOCEILING_OFFSET"]),
                    "gradient_factor_99": _u8(record, C["GF99_OFFSET"]),
                    "at_plus_five_raw": at_plus_five_raw,
                    "respiratory_minute_volume_raw": rmv_raw,
                },
            )
            samples.append(sample)
            last_sample = sample
            logical_index += 1

        elif _SAMPLE_EXT_TYPE and record_type == _SAMPLE_EXT_TYPE and last_sample is not None:
            ext = last_sample.values.setdefault("extension", {})
            ext["wai_sensor2_pressure"] = _u16_be(record, C["SAMPLE_EXT_WAI_SENSOR_2_1ST_BYTE_OFFSET"])
            ext["wai_sensor3_pressure"] = _u16_be(record, C["SAMPLE_EXT_WAI_SENSOR_3_1ST_BYTE_OFFSET"])
            ext["hp_diluent_pressure"] = _u16_be(record, C["SAMPLE_EXT_HPDIL_1ST_BYTE_OFFSET"])
            ext["hp_o2_pressure"] = _u16_be(record, C["SAMPLE_EXT_HPO2_1ST_BYTE_OFFSET"])
            ext["raw"] = record

    return samples


def decode_petrel_v14(data: bytes | bytearray | None) -> Dict[str, Any]:
    """Decode a Petrel v14 payload into structured components."""

    if not data:
        return {"samples": [], "raw_samples": []}

    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes-like")

    samples = decode_samples(bytes(data))
    return {
        "samples": [sample.values for sample in samples],
        "raw_samples": [sample.raw for sample in samples],
    }
