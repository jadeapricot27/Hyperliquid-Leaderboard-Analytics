"""Sparkline wrapper for a trader's equity curve."""

from __future__ import annotations

from textual.widgets import Sparkline


class EquitySpark(Sparkline):
    """Exposes a semantic ``update_curve`` over Sparkline's reactive ``data``."""

    def update_curve(self, points: list[float]) -> None:
        self.data = points if points else [1.0]
