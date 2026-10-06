"""Board pane — the ranked leaderboard table + movers strip."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from hl_leaderboard_analytics.core.models import BoardSnapshot
from hl_leaderboard_analytics.tui.widgets import BoardTable, MoversStrip


class BoardPane(Vertical):
    DEFAULT_CSS = """
    BoardPane { padding: 1 2; }
    BoardPane BoardTable { height: 1fr; margin-top: 1; }
    BoardPane MoversStrip { height: auto; margin-top: 1; padding: 1 1; border: round $panel; }
    """

    def show(self, snapshot: BoardSnapshot) -> None:
        f = snapshot.filter
        self.query_one("#board-meta", Static).update(
            f"Window: [bold]{f.window}[/]   Sort: [bold]{f.sort} ↓[/]   "
            f"Asset: [bold]{f.asset or 'ALL'}[/]   Lev: [bold]{f.lev_min:g}-{f.lev_max:g}[/]   "
            f"[dim]{snapshot.total_traders} traders, {len(snapshot.rows)} shown[/]"
        )
        self.query_one(BoardTable).show_rows(snapshot.rows)
        self.query_one(MoversStrip).show(snapshot.movers)

    def compose(self) -> ComposeResult:
        yield Static("🏆  LEADERBOARD", classes="pane-title")
        yield Static(id="board-meta")
        yield BoardTable()
        yield MoversStrip()
