"""Helpers for decoding binary payloads from Shearwater logs."""

from __future__ import annotations

import base64
import binascii
import gzip
import json
import struct
from typing import Any, Dict, List, Sequence, Tuple


_PO2_RANGE = (0.2, 2.0)
_SENSOR_COUNT = 3


def decompress_petrel_blob(blob_bytes: bytes) -> bytes:
    """Return the decompressed Petrel payload contained in *blob_bytes*."""

    if not blob_bytes:
        return b""

    data = bytes(blob_bytes)
    if len(data) >= 4 and data[:4] in {b"\x00-\x00\x00", b"\x00-\x00\x08"}:
        data = data[4:]

    header_index = data.find(b"\x1f\x8b")
    if header_index == -1:
        return b""
    if header_index:
        data = data[header_index:]

    try:
        return gzip.decompress(data)
    except OSError:
        return b""


def _extract_float_stream(blob_bytes: bytes) -> Tuple[float, ...]:
    """Return the raw float stream embedded in the Petrel payload."""

    raw = decompress_petrel_blob(blob_bytes)
    if not raw:
        return tuple()

    if len(raw) % 4:
        raw = raw[: len(raw) - (len(raw) % 4)]

    float_count = len(raw) // 4
    if not float_count:
        return tuple()

    return struct.unpack(f"<{float_count}f", raw)



def decode_petrel_raw_floats(blob_bytes: bytes) -> Tuple[float, ...]:
    """Return the full sequence of floats in *blob_bytes* without filtering."""

    return _extract_float_stream(blob_bytes)


def decode_petrel_frames(
    blob_bytes: bytes, *, sensor_count: int = _SENSOR_COUNT
) -> Tuple[Tuple[float, ...], ...]:
    """Return tuples of raw samples grouped per sensor reading."""

    floats = decode_petrel_raw_floats(blob_bytes)
    if not floats or sensor_count <= 0:
        return tuple()

    frames: List[Tuple[float, ...]] = []
    total = len(floats)
    for index in range(0, total - (total % sensor_count), sensor_count):
        frame = tuple(floats[index : index + sensor_count])
        if len(frame) == sensor_count:
            frames.append(frame)

    return tuple(frames)


def decode_metadata_blob(blob_bytes: bytes) -> Dict[str, Any]:
    """Return JSON metadata embedded in *blob_bytes* with optional raw bytes.

    *data_bytes_2* and *data_bytes_3* are stored as UTF-8 JSON blobs.  This
    helper decodes the JSON and, when a ``RawBytes`` field is present, expands
    it into a ``raw_bytes`` entry containing the decoded bytes for inspection.
    """

    if not blob_bytes:
        return {}

    text = bytes(blob_bytes).decode("utf-8", errors="replace")
    try:
        payload: Dict[str, Any] = json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}

    raw_b64 = payload.get("RawBytes")
    if isinstance(raw_b64, str):
        try:
            payload["raw_bytes"] = base64.b64decode(raw_b64)
        except (binascii.Error, ValueError):
            pass

    return payload


__all__ = [
    "decode_petrel_raw_floats",
    "decode_petrel_frames",
    "decompress_petrel_blob",
    "decode_metadata_blob",
]
