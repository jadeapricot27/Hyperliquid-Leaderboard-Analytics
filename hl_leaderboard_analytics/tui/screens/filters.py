"""Filters pane — current filter spec + how to change it."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from hl_leaderboard_analytics.core.models import FilterSpec


class FiltersPane(VerticalScroll):
    DEFAULT_CSS = """
    FiltersPane { padding: 1 2; }
    """

    def show(self, spec: FilterSpec) -> None:
        self.query_one("#filter-block", Static).update(
            f"[bold cyan]window[/]      = [bold]{spec.window}[/]\n"
            f"[bold cyan]sort[/]        = [bold]{spec.sort}[/]   [dim](s to cycle)[/]\n"
            f"[bold cyan]asset[/]       = [bold]{spec.asset or 'ALL'}[/]\n"
            f"[bold cyan]lev band[/]    = [bold]{spec.lev_min:g}-{spec.lev_max:g}[/]\n"
            f"[bold cyan]limit[/]       = [bold]{spec.limit}[/]\n\n"
            "[dim]Press [/][bold]s[/][dim] cycle sort · [/][bold]w[/][dim] cycle window · "
            "[/][bold]/[/][dim] filter alias · reload via CLI flags[/]"
        )

    def compose(self) -> ComposeResult:
        yield Static("🔪  FILTERS & SORT", classes="pane-title")
        yield Static(id="filter-block")
