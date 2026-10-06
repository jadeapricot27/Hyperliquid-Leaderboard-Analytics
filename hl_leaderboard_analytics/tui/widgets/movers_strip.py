"""A Static that renders the top gainers / losers strip."""

from __future__ import annotations

from textual.widgets import Static

from hl_leaderboard_analytics.core.models import MoverRecord


class MoversStrip(Static):
    """``▲ alias +18.4%   ▼ alias −24.1% …``"""

    def show(self, movers: list[MoverRecord]) -> None:
        up = [m for m in movers if m.direction == "up"][:5]
        down = [m for m in movers if m.direction == "down"][:5]
        up_str = "   ".join(
            f"[bold green]▲ {m.alias}[/] [green]{m.delta_24h * 100:+.1f}%[/]" for m in up
        ) or "[dim]—[/]"
        down_str = "   ".join(
            f"[bold red]▼ {m.alias}[/] [red]{m.delta_24h * 100:+.1f}%[/]" for m in down
        ) or "[dim]—[/]"
        self.update(f"TOP MOVERS (24h proxy)\n{up_str}\n{down_str}")
