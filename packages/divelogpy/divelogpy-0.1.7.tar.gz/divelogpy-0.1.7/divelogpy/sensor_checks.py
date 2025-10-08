"""Time series helpers for decoded dive samples."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, List, Mapping, Sequence, Tuple
from .models import Sensor
from typing import Union
import pandas as pd
import numpy as np

SensorData = Union[Sensor,pd.Series
                   ]
def add_sensor_noise(s:SensorData, std_mV: float = 1.0, seed: int | None = None) -> pd.Series:
    """
    Add continuous Gaussian noise (zero mean, std=std_mV) to the sensor readings.
    This increases variance realistically.
    """
    if isinstance(s,Sensor):
        s=s.milivolts
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=0.0, scale=std_mV, size=len(s))
    return pd.Series(s.values + noise, index=s.index, name=f"{s.name}_noisy")

def add_current_limiting_to_sensor(s:SensorData, upper_limit:float) -> pd.Series:
    """
    Clip sensor readings to an upper limit to simulate current limiting.
    """
    if isinstance(s,Sensor):
        s=s.milivolts
    return pd.Series(s.clip(upper=upper_limit), index=s.index, name=f"{s.name}_clipped")