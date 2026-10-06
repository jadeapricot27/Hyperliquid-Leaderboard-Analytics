"""Detail pane — equity curve, per-asset breakdown, key stats for one trader."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from hl_leaderboard_analytics.core.mock_data import equity_curve
from hl_leaderboard_analytics.core.models import LeaderboardRow
from hl_leaderboard_analytics.tui.widgets import AssetBreakdown, EquitySpark


class DetailPane(Vertical):
    DEFAULT_CSS = """
    DetailPane { padding: 1 2; }
    DetailPane EquitySpark { height: 6; margin: 1 0; border: round $accent; }
    DetailPane AssetBreakdown { height: auto; padding: 1 1; border: round $panel; }
    """

    def show(self, row: LeaderboardRow) -> None:
        w = row.windows.get("90d")
        self.query_one("#detail-meta", Static).update(
            f"[bold]{row.alias}[/]   [dim]{row.short}[/]   "
            f"lev [bold]{row.leverage:.1f}x[/]   side-bias [bold]{row.side_bias:+.2f}[/]"
        )
        self.query_one("#detail-stats", Static).update(self._stats_block(row))
        self.query_one(EquitySpark).update_curve(equity_curve(row))
        self.query_one(AssetBreakdown).show(row.top_assets)

    @staticmethod
    def _stats_block(row: LeaderboardRow) -> str:
        lines = []
        for label in ("7d", "30d", "90d", "all"):
            w = row.windows.get(label)
            if not w:
                continue
            lines.append(
                f"[bold cyan]{label:4}[/]  ROI [green]{w.roi * 100:+6.1f}%[/]  "
                f"vol {w.volume / 1e6:5.2f}M  win {w.win_rate * 100:4.1f}%  "
                f"Sharpe {w.sharpe:4.2f}  PF {w.profit_factor:4.2f}  "
                f"DD [red]{w.max_drawdown * 100:+6.1f}%[/]  trades {w.trades}"
            )
        return "\n".join(lines)

    def compose(self) -> ComposeResult:
        yield Static("📈  TRADER DETAIL", classes="pane-title")
        yield Static(id="detail-meta")
        yield Static(id="detail-stats")
        yield Static("[dim]EQUITY CURVE (90d)[/]")
        yield EquitySpark()
        yield Static("[dim]PER-ASSET PnL BREAKDOWN[/]")
        yield AssetBreakdown()
