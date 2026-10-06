"""Compare pane — 7d vs 30d vs 90d side-by-side for the focused trader."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static

from hl_leaderboard_analytics.core.models import LeaderboardRow


class ComparePane(Vertical):
    DEFAULT_CSS = """
    ComparePane { padding: 1 2; }
    ComparePane DataTable { margin-top: 1; height: auto; }
    """

    def show(self, row: LeaderboardRow) -> None:
        self.query_one("#compare-meta", Static).update(
            f"Comparing periods for [bold]{row.alias}[/]   [dim]{row.short}[/]"
        )
        table = self.query_one(DataTable)
        table.clear()
        for label in ("7d", "30d", "90d", "all"):
            w = row.windows.get(label)
            if not w:
                continue
            table.add_row(
                label,
                f"{w.roi * 100:+.1f}%",
                f"{w.volume / 1e6:.2f}M",
                f"{w.win_rate * 100:.1f}%",
                f"{w.sharpe:.2f}",
                f"{w.profit_factor:.2f}",
                f"{w.max_drawdown * 100:+.1f}%",
                str(w.trades),
            )

    def compose(self) -> ComposeResult:
        yield Static("📅  PERIOD COMPARE (7d · 30d · 90d · all)", classes="pane-title")
        yield Static(id="compare-meta")
        table = DataTable(cursor_type="row", zebra_stripes=True)
        table.add_columns("Window", "ROI", "Volume", "Win%", "Sharpe", "PF", "MaxDD", "Trades")
        yield table
