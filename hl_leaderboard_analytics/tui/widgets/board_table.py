"""The main leaderboard table."""

from __future__ import annotations

from textual.widgets import DataTable

from hl_leaderboard_analytics.core.models import LeaderboardRow


def _pct(x: float) -> str:
    return f"{x * 100:+.1f}%" if x else "0.0%"


class BoardTable(DataTable):
    """Ranks traders for the active window + sort."""

    def __init__(self) -> None:
        super().__init__(cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:  # type: ignore[override]
        self.add_columns(
            "#", "Alias", "Address", "ROI(90d)", "ROI(30d)",
            "Volume", "Win%", "Sharpe", "PF", "MaxDD",
        )

    def show_rows(self, rows: list[LeaderboardRow]) -> None:
        self.clear()
        for r in rows:
            w90 = r.windows.get("90d")
            w30 = r.windows.get("30d")
            self.add_row(
                str(r.rank),
                r.alias,
                r.short,
                _pct(w90.roi) if w90 else "—",
                _pct(w30.roi) if w30 else "—",
                f"{(w90.volume / 1e6):.2f}M" if w90 else "—",
                f"{w90.win_rate * 100:.1f}" if w90 else "—",
                f"{w90.sharpe:.2f}" if w90 else "—",
                f"{w90.profit_factor:.2f}" if w90 else "—",
                _pct(w90.max_drawdown) if w90 else "—",
                key=r.address,
            )
