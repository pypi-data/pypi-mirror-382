"""Plotting helpers for dive visualisations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Sequence

import matplotlib.pyplot as plt

try:  # optional dependency
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover - optional dependency
    go = None

import pandas as _pd
import numpy as np

from .models import Dive
import pandas as pd


@dataclass
class _ScaleField:
    field: str
    label: str | None = None
    color: str | None = None
    dash: str | None = None
    width: float | None = None


@dataclass
class _ScaleGroup:
    fields: List[_ScaleField]
    title: str | None = None
    side: str | None = None
    range: Sequence[float] | None = None
    axis: Mapping[str, object] | None = None


def _ensure_plotly():
    if go is None:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("Plotly is required for interactive timeseries plotting. Install it with 'pip install plotly'.")


def _normalise_scale_groups(scale_groups: Sequence[object] | None) -> List[_ScaleGroup]:
    if not scale_groups:
        return []

    palette = [
        "#FF851B",
        "#FF4136",
        "#2ECC40",
        "#FFDC00",
        "#0074D9",
        "#B10DC9",
    ]

    palette_index = 0

    result: List[_ScaleGroup] = []
    for group in scale_groups:
        if isinstance(group, str):
            group_map: Mapping[str, object] = {"fields": [group]}
        elif isinstance(group, Mapping):
            group_map = group
        elif isinstance(group, Sequence) and not isinstance(group, (bytes, bytearray)):
            group_map = {"fields": list(group)}
        else:
            raise TypeError(
                "Each scale group must be a mapping of options, a list/tuple of field names, or a single field name."
            )

        raw_fields = group_map.get("fields")
        if not raw_fields:
            raise ValueError("Scale group requires a non-empty 'fields' list.")

        normalised_fields: List[_ScaleField] = []
        for payload in raw_fields:
            if isinstance(payload, str):
                payload_map = {"field": payload}
            elif isinstance(payload, Mapping):
                payload_map = dict(payload)
            else:
                raise TypeError("Scale group fields must be either field names or mapping descriptors.")

            field_name = payload_map.get("field")
            if not field_name:
                raise ValueError("Scale group field descriptors must include a 'field' entry.")

            color = payload_map.get("color")
            if color is None:
                color = palette[palette_index % len(palette)]
                palette_index += 1

            normalised_fields.append(
                _ScaleField(
                    field=field_name,
                    label=payload_map.get("label"),
                    color=color,
                    dash=payload_map.get("dash"),
                    width=payload_map.get("width"),
                )
            )

        result.append(
            _ScaleGroup(
                fields=normalised_fields,
                title=group_map.get("title"),
                side=group_map.get("side"),
                range=group_map.get("range"),
                axis=group_map.get("axis"),
            )
        )

    return result


import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_sensor_strip(
    df: pd.DataFrame,
    sensor_cols: tuple[str, str, str] = (
        "sensor1_millivolts",
        "sensor2_millivolts",
        "sensor3_millivolts",
    ),
    *,
    template: str = "plotly_dark",
    figure_title: str | None = "Lag-1 Scatter: Sensors",
    marker_size: int = 5,
    marker_opacity: float = 0.8,
    show_identity_line: bool = True,
    identity_line_width: int = 1,
    identity_line_dash: str = "dash",
) -> "go.Figure":
    """
    Plot 3-panel lag-1 scatter (y[t] vs y[t-1]) for the given sensor columns.

    Parameters
    ----------
    df:
        DataFrame containing sensor millivolt columns.
    sensor_cols:
        Tuple of exactly three column names (sensor1, sensor2, sensor3).
    template / figure_title:
        Plotly template and optional title.
    marker_* / identity_*:
        Styling for points and the y=x reference line.
    """

    # Basic column presence check (lightweight; fail fast)
    missing = [c for c in sensor_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in df: {', '.join(missing)}")

    # Build per-sensor lag-1 DataFrames and aggregate for global axis range
    lagged_frames = []
    all_x, all_y = [], []
    for c in sensor_cols:
        s = pd.to_numeric(df[c], errors="coerce")
        d = pd.DataFrame({"x": s.shift(1), "y": s}).dropna()
        lagged_frames.append((c, d))
        if not d.empty:
            all_x.append(d["x"].values)
            all_y.append(d["y"].values)

    # Global symmetric axis range across all panels
    if all_x:
        all_x = np.concatenate(all_x)
        all_y = np.concatenate(all_y)
        lim_min = float(np.nanmin([all_x.min(), all_y.min()]))
        lim_max = float(np.nanmax([all_x.max(), all_y.max()]))
        pad = 0.03 * (lim_max - lim_min if lim_max > lim_min else 1.0)
        axis_range = [lim_min - pad, lim_max + pad]
    else:
        axis_range = None

    fig = make_subplots(
        rows=1, cols=3,
        horizontal_spacing=0.06,
        subplot_titles=[c.replace("_", " ") for c in sensor_cols],
    )

    for i, (c, d) in enumerate(lagged_frames, start=1):
        # Scatter points
        fig.add_trace(
            go.Scatter(
                x=d["x"], y=d["y"],
                mode="markers",
                name=c, showlegend=False,
                marker=dict(size=marker_size, opacity=marker_opacity),
                hovertemplate=f"{c}[t-1]=%{{x:.6g}}<br>{c}[t]=%{{y:.6g}}<extra></extra>",
            ),
            row=1, col=i
        )

        # Identity line
        if show_identity_line and axis_range is not None:
            fig.add_trace(
                go.Scatter(
                    x=axis_range, y=axis_range,
                    mode="lines",
                    name="y = x",
                    line=dict(width=identity_line_width, dash=identity_line_dash),
                    hoverinfo="skip",
                    showlegend=(i == 1),  # show once
                ),
                row=1, col=i
            )

        # Correlation annotation in the subplot title
        if not d.empty and d["x"].std(ddof=1) > 0 and d["y"].std(ddof=1) > 0:
            rho = float(np.corrcoef(d["x"], d["y"])[0, 1])
            fig.layout.annotations[i-1].text = f"{c.replace('_',' ')} (ρ = {rho:.3f})"

        # Axes (equal aspect)
        fig.update_xaxes(
            title_text=f"{c}[t-1]",
            zeroline=False, showgrid=False,
            range=axis_range,
            row=1, col=i
        )
        fig.update_yaxes(
            title_text=f"{c}[t]" if i == 1 else None,
            zeroline=False, showgrid=False,
            scaleanchor=f"x{i}", scaleratio=1,
            range=axis_range,
            row=1, col=i
        )

    fig.update_layout(
        template=template,
        title=figure_title or "Lag-1 Scatter: Sensors",
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        margin=dict(l=50, r=20, t=60, b=40),
    )
    return fig


def plot_timeseries(
    timeseries,
    *,
    include_depth: bool = True,
    depth_field: str | None = None,
    depth_label: str | None = None,
    depth_color: str = "#1f77b4",
    depth_fillcolor: str = "rgba(31, 119, 180, 0.25)",
    depth_side: str = "left",
    scale_groups: Sequence[Mapping[str, object]] | None = None,
    template: str = "plotly_dark",
    time_units: str = "minutes",
    time_axis_label: str | None = None,
    figure_title: str | None = None,
) -> "go.Figure":
    """Render an interactive Plotly figure for a dive timeseries.

    Parameters
    ----------
    timeseries:
        Either a :class:`divelogpy.timeseries.DiveTimeSeries` instance or any
        object that exposes ``to_df`` with a matching signature.
    include_depth:
        When True (default) the depth trace is added as the primary axis.
    depth_field:
        Optional override for the depth column to display. When omitted the
        function prefers ``depth_ft`` then ``depth_m`` if present.
    depth_label:
        Custom axis label for depth. If omitted a label derived from the depth
        field is used.
    depth_color / depth_fillcolor:
        Styling for the depth trace and area fill.
    depth_side:
        Position of the depth axis (``'left'`` or ``'right'``).
    scale_groups:
        Sequence describing additional y-axes. Each element may be one of:

        * A single field name (``"average_ppo2"``)
        * A list/tuple of field names (``["average_ppo2", "ppo2_setpoint"]``)
        * A mapping with ``fields`` and optional styling keys (``{"fields": [...], "title": "ppO₂"}``).

        Field descriptors within a mapping can override ``label``, ``color``,
        ``dash`` and ``width`` for each trace. Group-level options include
        ``title`` (axis label), ``side`` (``"left"``/``"right"``), ``range`` and
        ``axis`` (dict of raw Plotly axis layout overrides, e.g. ``{"overlaying": None}``).
        When omitted no additional axes are drawn.
    template:
        Plotly template, defaults to ``plotly_dark``.
    time_units:
        Units for the x-axis; either ``'minutes'`` (default) or ``'seconds'``.
    time_axis_label:
        Optional label for the x-axis. If omitted a label is derived from
        ``time_units``.
    figure_title:
        Optional figure title.
    """

    _ensure_plotly()

    groups = _normalise_scale_groups(scale_groups)

    df = _coerce_timeseries_dataframe(timeseries, None, include_time=True)
    available_set = set(df.reset_index().columns)
    if "time_seconds" not in available_set:
        raise ValueError("Timeseries data must include a 'time_seconds' column.")

    depth_candidates: Iterable[str]
    if depth_field:
        depth_candidates = (depth_field,)
    else:
        depth_candidates = ("depth_ft", "depth_m", "depth")

    chosen_depth_field = None
    derived_label = depth_label
    if include_depth:
        for candidate in depth_candidates:
            if candidate is None:
                continue
            if available_set is not None and candidate not in available_set:
                continue
            chosen_depth_field = candidate
            break
        if chosen_depth_field is None:
            raise ValueError("Depth data was requested but no depth field was supplied or discovered.")

    required_fields = {field.field for group in groups for field in group.fields}
    if include_depth and chosen_depth_field:
        required_fields.add(chosen_depth_field)

    if not required_fields:
        raise ValueError("No fields were provided to plot. Supply scale groups or enable depth.")

    subset_columns = [*sorted(required_fields)]
    if df.index.name != 'time_seconds':
        subset_columns.insert(0, "time_seconds") 
    missing_subset = [col for col in subset_columns if col not in df.reset_index().columns]
    if missing_subset:
        raise ValueError(f"Timeseries data is missing required columns: {', '.join(missing_subset)}")

    df = df[subset_columns].reset_index().rename(columns={"time_seconds": "seconds"})
    if "seconds" not in df.columns:
        raise ValueError("Timeseries must expose a 'time_seconds' column when converted to a DataFrame.")
    seconds_series = df["seconds"].astype(float)

    time_units_normalised = time_units.lower()
    if time_units_normalised == "seconds":
        time_values = seconds_series
        xaxis_title = time_axis_label or "Time (s)"
    elif time_units_normalised == "minutes":
        time_values = seconds_series / 60.0
        xaxis_title = time_axis_label or "Time (min)"
    else:
        raise ValueError("time_units must be either 'seconds' or 'minutes'.")

    fig = go.Figure()

    depth_side_normalised = depth_side.lower()
    if depth_side_normalised not in {"left", "right"}:
        raise ValueError("depth_side must be either 'left' or 'right'.")

    if include_depth and chosen_depth_field:
        if chosen_depth_field not in df.columns:
            raise ValueError(f"Depth field '{chosen_depth_field}' is not present in the timeseries data.")
        derived_label = depth_label
        if derived_label is None:
            if chosen_depth_field.endswith("_ft"):
                derived_label = "Depth (ft)"
            elif chosen_depth_field.endswith("_m"):
                derived_label = "Depth (m)"
            else:
                derived_label = "Depth"

        fig.add_trace(
            go.Scatter(
                x=time_values,
                y=df[chosen_depth_field],
                mode="lines",
                name=derived_label,
                line=dict(color=depth_color, width=2),
                fill="tozeroy",
                fillcolor=depth_fillcolor,
                hovertemplate="%{y:.2f}<extra>" + derived_label + "</extra>",
            )
        )

    axis_layout: dict[str, object] = {
        "template": template,
        "xaxis": dict(title=xaxis_title, zeroline=False),
        "legend": dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
    }

    has_primary_axis = include_depth and chosen_depth_field is not None
    if has_primary_axis:
        axis_layout["yaxis"] = dict(title=depth_label or derived_label, autorange="reversed", side=depth_side_normalised)
    else:
        axis_layout["yaxis"] = dict(title="Value", side="left")

    next_axis_index = 2 if has_primary_axis else 1

    for idx, group in enumerate(groups):
        if not has_primary_axis and idx == 0:
            axis_name = "y"
            axis_key = "yaxis"
            axis_config = {"side": (group.side or "left").lower()}
        else:
            axis_name = f"y{next_axis_index}"
            axis_key = f"yaxis{next_axis_index}"
            axis_config = {"overlaying": "y", "side": (group.side or "right").lower()}
            axis_layout[axis_key] = {}
            next_axis_index += 1

        if group.title:
            axis_config["title"] = group.title
        if group.range:
            axis_config["range"] = list(group.range)
        if group.axis:
            axis_config.update(group.axis)

        overlaying_value = axis_config.get("overlaying", None)
        if overlaying_value is None:
            axis_config.pop("overlaying", None)

        axis_layout.setdefault(axis_key, {}).update(axis_config)

        for field in group.fields:
            column = field.field
            if column not in df.columns:
                raise ValueError(f"Field '{column}' is not available in the timeseries DataFrame.")
            trace_kwargs = dict(
                x=time_values,
                y=df[column],
                mode="lines",
                name=field.label or column,
                line=dict(color=field.color, dash=field.dash, width=field.width or 2),
            )
            if axis_name != "y":
                trace_kwargs["yaxis"] = axis_name
            fig.add_trace(go.Scatter(**trace_kwargs))

    if figure_title:
        axis_layout["title"] = figure_title

    fig.update_layout(**axis_layout)

    return fig


def plot_po2_millivolts_scatter(
    timeseries,
    *,
    average_field: str = "average_ppo2",
    sensor_fields: Sequence[str] | None = None,
    include_setpoint: bool = True,
    template: str = "plotly_dark",
    figure_title: str | None = None,
) -> "go.Figure":
    """Plot sensor millivolts against average ppO₂ for correlation checks.

    Parameters
    ----------
    timeseries:
        Dive timeseries object (with ``to_df``/``available_fields``) or a
        Pandas DataFrame containing the requested columns along with a
        ``time_seconds`` column.
    average_field:
        Column name to use for the ppO₂ value on the x-axis. Defaults to
        ``"average_ppo2"``.
    sensor_fields:
        Optional list of sensor millivolt columns. When omitted the function
        automatically discovers columns matching ``sensor*_millivolts``.
    include_setpoint:
        When True, a hover column for ``ppo2_setpoint`` is added when present.
    template:
        Plotly template for styling.
    figure_title:
        Optional title for the figure.
    """

    _ensure_plotly()

    df = _coerce_timeseries_dataframe(timeseries, None, include_time=True)
    available_columns = set(df.columns)

    if sensor_fields is None:
        sensor_fields = sorted(
            field
            for field in available_columns
            if isinstance(field, str) and field.startswith("sensor") and field.endswith("_millivolts")
        )

    if not sensor_fields:
        raise ValueError("No sensor millivolt columns were supplied or discovered.")

    missing_sensors = [field for field in sensor_fields if field not in available_columns]
    if missing_sensors:
        raise ValueError(f"Sensor fields not present in timeseries: {', '.join(missing_sensors)}")

    if average_field not in available_columns:
        raise ValueError(f"Average field '{average_field}' is not present in the timeseries data.")

    hover_fields: list[str] = []
    if include_setpoint and "ppo2_setpoint" in available_columns:
        hover_fields.append("ppo2_setpoint")

    subset_columns = [average_field, *sensor_fields, *hover_fields]
    index_is_time = df.index.name == "time_seconds"
    if not index_is_time:
        subset_columns.insert(0, "time_seconds")
    missing_subset = [col for col in subset_columns if col not in df.columns]
    if missing_subset:
        raise ValueError(f"Timeseries data is missing required columns: {', '.join(missing_subset)}")

    df = df[subset_columns].copy()
    if index_is_time:
        df = df.reset_index()
    else:
        df = df.reset_index(drop=True)
    df["time_seconds"] = df["time_seconds"].astype(float)

    drop_columns = [average_field, *sensor_fields]
    df = df.dropna(subset=drop_columns).copy()
    if df.empty:
        raise ValueError("No rows remain after dropping NA values for the selected fields.")

    long_frames = []
    for field in sensor_fields:
        sensor_label = field.replace("_millivolts", "").replace("sensor", "Sensor ")
        frame = df[[average_field, field, "time_seconds", *hover_fields]].copy()
        frame["sensor"] = sensor_label
        frame.rename(columns={field: "millivolts"}, inplace=True)
        long_frames.append(frame)

    combined = _pd.concat(long_frames, ignore_index=True)

    fig = go.Figure()

    palette = [
        "#FF851B",
        "#FF4136",
        "#2ECC40",
        "#FFDC00",
        "#0074D9",
        "#B10DC9",
    ]

    for idx, (sensor, group) in enumerate(combined.groupby("sensor", sort=False)):
        color = palette[idx % len(palette)]
        hovertemplate = "Average ppO₂: %{x:.3f}<br>Millivolts: %{y:.1f}<br>Time: %{customdata[0]:.0f}s"
        customdata = group[["time_seconds"] + hover_fields].to_numpy()
        fig.add_trace(
            go.Scatter(
                x=group[average_field],
                y=group["millivolts"],
                mode="markers",
                name=sensor,
                marker=dict(color=color, size=6, opacity=0.65),
                customdata=customdata,
                hovertemplate=hovertemplate + ("<br>Setpoint: %{customdata[1]:.2f}" if hover_fields else "") + "<extra></extra>",
            )
        )

    fig.update_layout(
        template=template,
        title=figure_title or "Sensor Millivolts vs Average ppO₂",
        xaxis=dict(title="Average ppO₂ (ATA)", zeroline=False),
        yaxis=dict(title="Sensor millivolts (mV)", zeroline=False),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
    )

    return fig

def plot_sensor_millivolts_by_ppo2_heatmap(
    dive_client,
    *,
    sensor: int | str = "sensor1_millivolts",
    start: str | _pd.Timestamp | None = None,
    end: str | _pd.Timestamp | None = None,
    bin_size: float = 0.1,
    template: str = "plotly_dark",
    figure_title: str | None = None,
) -> "go.Figure":
    """Display a ppO₂-bin heatmap for the first CCR dive of each day."""

    _ensure_plotly()

    if isinstance(sensor, int):
        if sensor < 1:
            raise ValueError("Sensor index must be >= 1.")
        sensor_field = f"sensor{sensor}_millivolts"
    else:
        sensor_field = str(sensor)

    if bin_size <= 0:
        raise ValueError("bin_size must be positive.")

    start_day = _normalize_date(start)
    end_day = _normalize_date(end)

    ccr_dives = [
        dive
        for dive in dive_client.get_primary_computer_dives()
        if getattr(dive, "mode", "").lower() == "ccr"
    ]

    records: list[_pd.Series] = []
    ppo2_min, ppo2_max = float('inf'), float('-inf')

    for dive in ccr_dives:
        if dive.timeseries is None:
            continue
        try:
            ts = _coerce_timeseries_dataframe(dive.timeseries, [sensor_field, "average_ppo2"], include_time=False)
        except (ValueError, TypeError):
            continue

        ts = ts[[sensor_field, "average_ppo2"]].dropna()
        if ts.empty:
            continue

        ts["ppo2_bin"] = np.round(np.floor(ts["average_ppo2"] / bin_size) * bin_size, 3)
        grouped = ts.groupby("ppo2_bin")[sensor_field].mean()
        if grouped.empty:
            continue

        ppo2_min = min(ppo2_min, grouped.index.min())
        ppo2_max = max(ppo2_max, grouped.index.max())

        series = grouped.copy()
        series.name = _pd.Timestamp(dive.start)
        records.append(series)

    if not records:
        raise ValueError("No CCR dives with the requested sensor data were found.")

    matrix = _pd.DataFrame(records)
    matrix.index = _pd.to_datetime(matrix.index)
    matrix.index.name = "start"

    if start_day is not None or end_day is not None:
        matrix = matrix.loc[start_day:end_day]

    if matrix.empty:
        raise ValueError("No data is available within the requested date range.")

    first_per_day = (
        matrix.sort_index()
        .groupby(matrix.index.normalize())
        .first()
    )

    bin_start = np.floor(ppo2_min / bin_size) * bin_size
    bin_end = np.ceil(ppo2_max / bin_size) * bin_size
    bins = np.round(np.arange(bin_start, bin_end + bin_size, bin_size), 3)

    first_per_day = first_per_day.reindex(columns=bins, fill_value=np.nan)

    labels = first_per_day.index.strftime("%Y-%m-%d").tolist()
    Z = first_per_day.to_numpy().T

    fig = go.Figure(
        data=go.Heatmap(
            x=labels,
            y=bins,
            z=Z,
            colorscale="Viridis",
            colorbar=dict(title="mV"),
            hovertemplate="Date: %{x}<br>ppO₂: %{y:.2f}<br>mV: %{z:.1f}<extra></extra>",
        )
    )

    fig.update_layout(
        template=template,
        title=figure_title or f"{sensor_field} millivolts by ppO₂ bin",
        xaxis=dict(type="category", title="Date", categoryorder="array", categoryarray=labels),
        yaxis=dict(title="ppO₂ (ATA)"),
        height=520,
        width=980,
        margin=dict(l=60, r=60, t=60, b=40),
    )

    return fig


def plot_sensor_usage_decay_heatmap(
    dive_client,
    *,
    target_ppo2: float = 1.2,
    bin_width_minutes: int = 30,
    min_total_ccr_minutes: float = 120.0,
    sensor_fields: Sequence[str] | None = None,
    start: str | _pd.Timestamp | None = None,
    end: str | _pd.Timestamp | None = None,
    template: str = "plotly_dark",
    figure_title: str | None = None,
) -> "go.Figure":
    """Display a cumulative CCR usage heatmap for sensor drift analysis."""

    _ensure_plotly()

    if bin_width_minutes <= 0:
        raise ValueError("bin_width_minutes must be positive.")
    if min_total_ccr_minutes < 0:
        raise ValueError("min_total_ccr_minutes must be non-negative.")

    start_day = _normalize_date(start)
    end_day = _normalize_date(end)

    ccr_dives = [
        dive
        for dive in dive_client.get_primary_computer_dives()
        if getattr(dive, "mode", "").lower() == "ccr"
    ]
    ccr_dives.sort(key=lambda d: d.start)

    if not ccr_dives:
        raise ValueError("No CCR dives found.")

    dives_by_day: dict[_pd.Timestamp, list[Dive]] = {}
    for dive in ccr_dives:
        day = _pd.Timestamp(dive.start).normalize()
        dives_by_day.setdefault(day, []).append(dive)

    totals = {
        day: sum((float(getattr(d, "duration_seconds", 0.0)) or 0.0) / 60.0 for d in dives)
        for day, dives in dives_by_day.items()
    }

    qualifying_days = {
        day
        for day, total in totals.items()
        if total >= min_total_ccr_minutes
        and (start_day is None or day >= start_day)
        and (end_day is None or day <= end_day)
    }

    if not qualifying_days:
        raise ValueError("No days meet the CCR usage threshold within the requested range.")

    if sensor_fields is None:
        sensor_fields = ["sensor1_millivolts", "sensor2_millivolts", "sensor3_millivolts"]
    sensor_fields = list(sensor_fields)

    target_bin = round(target_ppo2 * 10) / 10

    records: list[dict[str, object]] = []

    for day, dives in dives_by_day.items():
        if day not in qualifying_days:
            continue

        dives_sorted = sorted(dives, key=lambda d: d.start)
        offsets: dict[str, float] = {}
        cumulative = 0.0
        for dive in dives_sorted:
            offsets[dive.dive_id] = cumulative
            cumulative += (float(getattr(dive, "duration_seconds", 0.0)) or 0.0) / 60.0

        for dive in dives_sorted:
            if dive.timeseries is None:
                continue

            required = sensor_fields + ["average_ppo2"]
            try:
                ts = _coerce_timeseries_dataframe(dive.timeseries, required, include_time=True)
            except (ValueError, TypeError):
                continue

            ts = ts.dropna(subset=["average_ppo2"] + sensor_fields)
            if ts.empty:
                continue

            ts["usage_min"] = ts["time_seconds"].astype(float) / 60.0 + offsets.get(dive.dive_id, 0.0)
            ts["ppo2_bin"] = np.round(np.floor(ts["average_ppo2"] * 10) / 10, 1)
            ts["sensor_avg"] = ts[sensor_fields].mean(axis=1)

            ts_target = ts.loc[ts["ppo2_bin"] == round(target_bin, 1), ["sensor_avg", "usage_min"]]
            if ts_target.empty:
                continue

            ts_target["usage_bin_min"] = (
                np.floor(ts_target["usage_min"] / bin_width_minutes) * bin_width_minutes
            ).astype(int)

            grouped = ts_target.groupby("usage_bin_min")["sensor_avg"].mean()
            if grouped.empty:
                continue

            day_label = day.strftime("%Y-%m-%d")
            for usage_bin, mv in grouped.items():
                records.append({"day": day_label, "usage_bin_min": usage_bin, "mv": mv})

    if not records:
        raise ValueError("No qualifying data found for the requested ppO₂ bin and usage thresholds.")

    matrix = _pd.DataFrame.from_records(records)
    heat = (
        matrix.pivot_table(index="usage_bin_min", columns="day", values="mv", aggfunc="mean")
        .sort_index()
    )

    heat = heat.reindex(sorted(heat.index), axis=0)
    heat = heat.reindex(sorted(heat.columns, key=_pd.Timestamp), axis=1)

    y_bins = heat.index.to_list()
    x_labels = heat.columns.to_list()
    Z = heat.values

    fig = go.Figure(
        data=go.Heatmap(
            x=x_labels,
            y=y_bins,
            z=Z,
            colorscale="Viridis",
            colorbar=dict(title="mV"),
            hovertemplate="Day: %{x}<br>Usage: %{y} min<br>mV: %{z:.1f}<extra></extra>",
        )
    )

    fig.update_layout(
        template=template,
        title=figure_title
        or (
            f"Sensor average mV decay at ppO₂={target_ppo2:.1f}"
            f" (bins {bin_width_minutes}-min, days ≥ {min_total_ccr_minutes:.0f} min CCR)"
        ),
        xaxis=dict(type="category", title="Day"),
        yaxis=dict(title="Cumulative CCR usage (min)"),
        height=560,
        width=980,
        margin=dict(l=65, r=65, t=70, b=40),
    )

    return fig



def plot_what_if_setpoint(time_series: pd.DataFrame, setpoint: float, unlock_time_in_seconds: float):
    df = time_series.copy()
    df["atms"] = 1 + (df.depth_ft / 33)
    df["new_fo2"] = setpoint/ df.atms
    df["new_po2"] = df.loc[unlock_time_in_seconds :].apply(
        lambda row: (
            df.loc[unlock_time_in_seconds]["new_fo2"] * row["atms"] if row.name >= unlock_time_in_seconds else setpoint
        ),
        axis=1,
    )
    df.loc[: unlock_time_in_seconds, "new_po2"] = setpoint
    return plot_timeseries(
        df,
        scale_groups=[
            [
                "average_ppo2",
                "new_po2",
            ],  
        ],
    )

__all__ = [
    "plot_timeseries",
    "plot_po2_millivolts_scatter",
    "plot_sensor_millivolts_by_ppo2_heatmap",
    "plot_sensor_usage_decay_heatmap",
    "plot_what_if_setpoint",
    "plot_sensor_strip"
]
def _coerce_timeseries_dataframe(
    timeseries_or_df,
    required_fields: Sequence[str] | None = None,
    *,
    include_time: bool = True,
) -> _pd.DataFrame:
    fields_list = sorted(set(required_fields)) if required_fields else None

    if isinstance(timeseries_or_df, _pd.DataFrame):
        df = timeseries_or_df.copy()
        if required_fields:
            missing = set(required_fields) - set(df.columns)
            if missing:
                raise ValueError(
                    f"Timeseries DataFrame is missing required columns: {', '.join(sorted(missing))}"
                )
        if include_time and "time_seconds" not in df.columns:
            if "time_seconds" in df.index.names:
                df = df.reset_index()
            else:
                raise ValueError("Timeseries DataFrame must include a 'time_seconds' column when include_time is True.")
        return df

    if hasattr(timeseries_or_df, "to_df"):
        df = timeseries_or_df.to_df(fields_list, include_time=include_time)
        if df.empty:
            raise ValueError("The requested timeseries fields contain no data.")
        if include_time and "time_seconds" not in df.index.names and "time_seconds" not in df.columns:
            raise ValueError("Timeseries export must include 'time_seconds'.")
        if include_time and "time_seconds" not in df.columns:
            df = df.reset_index().rename(columns={"time_seconds": "time_seconds"})
        if required_fields:
            missing = set(required_fields) - set(df.columns)
            if missing:
                raise ValueError(
                    f"Timeseries export is missing required columns: {', '.join(sorted(missing))}"
                )
        return df

    raise TypeError("timeseries_or_df must be either a DataFrame or expose a 'to_df' method.")
def _normalize_date(value):
    if value is None:
        return None
    ts = _pd.Timestamp(value)
    if _pd.isna(ts):
        return None
    return ts.normalize()


def plot_noise_share(summary: pd.DataFrame, *, template: str = "plotly_dark") -> go.Figure:
    """
    Interactive pie chart showing how much of total noise variance
    each sensor contributes.
    Expects 'noise_var' column in summary DataFrame.
    """

    if "noise_var" not in summary.columns:
        raise ValueError("summary must include a 'noise_var' column")

    noise_share = summary["noise_var"] / summary["noise_var"].sum()

    fig = go.Figure(
        data=[
            go.Pie(
                labels=noise_share.index,
                values=noise_share,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Share: %{percent:.1%}<br>Noise Var: %{value:.2e}<extra></extra>",
                hole=0.3,
            )
        ]
    )

    fig.update_layout(
        title="Share of Total Noise Variance",
        template=template,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig