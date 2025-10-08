"""Programmatic generation of the sensor dashboard report as a PDF."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import plotly.io as pio

from . import client
from .models import Sensor, SensorCollection
from .plotting import (
    plot_sensor_millivolts_by_ppo2_heatmap,
    plot_sensor_usage_decay_heatmap,
)
from .sensor_checks import add_sensor_noise


@dataclass(frozen=True)
class ReportResult:
    """Container describing the generated report."""

    output_path: Path
    dive_id: str
    dive_start: Optional[datetime]
    dive_end: Optional[datetime]
    figure_count: int
    warnings: Tuple[str, ...]


class ReportGenerationError(RuntimeError):
    """Raised when the report cannot be produced."""


def _resolve_database_path(pathish: str | Path) -> Path:
    path = Path(pathish).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Database path does not exist: {path}")
    if path.is_dir():
        db_files = sorted(path.glob("*.db"), key=lambda p: p.stat().st_mtime)
        if not db_files:
            raise FileNotFoundError(f"Directory contains no .db files: {path}")
        return db_files[-1]
    if path.suffix.lower() != ".db":
        raise FileNotFoundError(f"Expected a '.db' file, received: {path}")
    return path


def _select_ccr_dive(
    dive_client: client.DiveLogClient,
    *,
    dive_id: str | None,
    dive_index: int,
):
    if dive_id:
        dive = dive_client.get_dive(dive_id)
        if dive is None:
            raise ReportGenerationError(f"No dive found for id '{dive_id}'.")
        return dive

    dives = [d for d in dive_client.get_primary_computer_dives() if getattr(d, "mode", "").lower() == "ccr"]
    if not dives:
        raise ReportGenerationError("No CCR dives available in the database.")

    try:
        return dives[dive_index]
    except IndexError as exc:  # pragma: no cover - defensive guard
        raise ReportGenerationError(
            f"CCR dive index {dive_index} is out of range for {len(dives)} available dives."
        ) from exc


def _prepare_sensor_collection(
    dive,
) -> SensorCollection:
    return dive.sensors


def _figure_to_png_bytes(fig, *, scale: float) -> bytes:
    return pio.to_image(fig, format="png", scale=scale)


def _append_plot(
    figures: List[Tuple[str, bytes]],
    warnings: List[str],
    title: str,
    builder: Callable[[], object],
    *,
    scale: float,
) -> None:
    try:
        fig = builder()
    except Exception as exc:  # pragma: no cover - defensive guard
        warnings.append(f"{title}: {exc}")
        return

    try:
        image_bytes = _figure_to_png_bytes(fig, scale=scale)
    except Exception as exc:  # pragma: no cover - defensive guard
        warnings.append(f"{title}: Failed to render figure ({exc}).")
        return

    figures.append((title, image_bytes))


def _add_text_page(pdf: PdfPages, title: str, lines: Sequence[str], *, font_size: int = 12) -> None:
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait in inches
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    ax.axis("off")

    ax.text(0.0, 1.0, title, fontsize=font_size + 4, fontweight="bold", va="top")
    y = 0.92
    for line in lines:
        ax.text(0.0, y, line, fontsize=font_size, va="top")
        y -= 0.05

    pdf.savefig(fig)
    plt.close(fig)


def _add_image_page(pdf: PdfPages, title: str, image_bytes: bytes, *, dpi: int) -> None:
    buffer = BytesIO(image_bytes)
    image = plt.imread(buffer, format="png")
    height, width = image.shape[:2]
    fig_width = width / dpi
    fig_height = height / dpi

    fig = plt.figure(figsize=(fig_width, fig_height))
    fig.suptitle(title, fontsize=12)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.imshow(image)
    ax.axis("off")
    pdf.savefig(fig)
    plt.close(fig)


def generate_sensor_report(
    database: str | Path,
    *,
    output: str | Path | None = None,
    dive_id: str | None = None,
    dive_index: int = -1,
    start: str | None = None,
    end: str | None = None,
    image_scale: float = 1.0,
    pdf_dpi: int = 300,
) -> ReportResult:
    """Produce the sensor dashboard PDF for a given database."""

    database_path = _resolve_database_path(database)
    output_path = Path(output) if output else database_path.with_name("sensor-report.pdf")

    with client.DiveLogClient(database_path) as dive_client:
        dive = _select_ccr_dive(dive_client, dive_id=dive_id, dive_index=dive_index)

        report_start = start
        report_end = end
        if report_start is None and getattr(dive, "start", None) is not None:
            report_start = (
                dive.start.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                .date()
                .isoformat()
            )
        if report_end is None and getattr(dive, "start", None) is not None:
            report_end = (
                dive.start.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
                .date()
                .isoformat()
            )

        sensors = _prepare_sensor_collection(
            dive)

        figures: List[Tuple[str, bytes]] = []
        warnings: List[str] = []

        _append_plot(
            figures,
            warnings,
            "Sensor Millivolt Time Series",
            builder=sensors.plot,
            scale=image_scale,
        )
        _append_plot(
            figures,
            warnings,
            "Sensor ppO2 vs Millivolts Scatter",
            builder=sensors.plot_po2_millivolts_scatter,
            scale=image_scale,
        )
        _append_plot(
            figures,
            warnings,
            "Sensor Noise Strip",
            builder=lambda: sensors.plot_sensor_noise(filter_low_setpoint=False),
            scale=image_scale,
        )
        _append_plot(
            figures,
            warnings,
            "Sensor Noise Share",
            builder=lambda: sensors.plot_noise_share(filter_low_setpoint=False),
            scale=image_scale,
        )

        for sensor_idx in range(1, 4):
            _append_plot(
                figures,
                warnings,
                f"Sensor {sensor_idx} mV by ppO2 Heatmap",
                builder=lambda idx=sensor_idx: plot_sensor_millivolts_by_ppo2_heatmap(
                    dive_client,
                    sensor=idx,
                    start=report_start,
                    end=report_end,
                ),
                scale=image_scale,
            )

        _append_plot(
            figures,
            warnings,
            "Sensor Usage Decay Heatmap",
            builder=lambda: plot_sensor_usage_decay_heatmap(
                dive_client,
                start=report_start,
                end=report_end,
            ),
            scale=image_scale,
        )

    if not figures:
        raise ReportGenerationError("All figure generation steps failed; nothing to include in the report.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(output_path) as pdf:
        dive_start = getattr(dive, "start", None)
        dive_end = getattr(dive, "end", None)
        summary_lines = [
            f"Database: {database_path}",
            f"Output: {output_path}",
            f"Dive ID: {getattr(dive, 'dive_id', 'N/A')}",
            f"Dive Start: {dive_start}",
            f"Dive End: {dive_end}",
            f"CCR Dive Selector: {'id=' + dive_id if dive_id else f'index={dive_index}'}",
            f"Report Window: {report_start or 'auto'} → {report_end or 'auto'}",
        ]
        if warnings:
            summary_lines.append("")
            summary_lines.append("Warnings:")
            summary_lines.extend(f"- {message}" for message in warnings)

        _add_text_page(pdf, "Sensor Dashboard Report", summary_lines)

        for title, image_bytes in figures:
            _add_image_page(pdf, title, image_bytes, dpi=pdf_dpi)

    return ReportResult(
        output_path=output_path,
        dive_id=getattr(dive, "dive_id", ""),
        dive_start=getattr(dive, "start", None),
        dive_end=getattr(dive, "end", None),
        figure_count=len(figures),
        warnings=tuple(warnings),
    )
