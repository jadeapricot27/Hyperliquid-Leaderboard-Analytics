"""Settings pane — render the active config."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from hl_leaderboard_analytics.config import Config


class SettingsPane(VerticalScroll):
    DEFAULT_CSS = """
    SettingsPane { padding: 1 2; }
    """

    def show(self, config: Config) -> None:
        n, b, e = config.network, config.board, config.export
        self.query_one("#cfg", Static).update(
            f"[bold cyan]network[/]\n"
            f"  [dim]api_url[/] = {n.api_url}\n"
            f"  [dim]timeout[/]  = {n.timeout_seconds}s   [dim]max_rps[/] = {n.max_rps}\n\n"
            f"[bold cyan]board[/]\n"
            f"  [dim]default_window[/] = {b.default_window}\n"
            f"  [dim]default_sort[/]   = {b.default_sort}\n"
            f"  [dim]page_size[/]      = {b.page_size}\n\n"
            f"[bold cyan]export[/]\n"
            f"  [dim]format[/]  = {e.format}\n"
            f"  [dim]out_dir[/] = {e.out_dir}\n\n"
            "[dim]Edit ~/.hl-leaderboard/config.toml and relaunch.[/]"
        )

    def compose(self) -> ComposeResult:
        yield Static("⚙️  SETTINGS", classes="pane-title")
        yield Static(id="cfg")
