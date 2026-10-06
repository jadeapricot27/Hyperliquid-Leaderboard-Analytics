"""The Textual application — the leaderboard analytics dashboard."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TabbedContent, TabPane

from hl_leaderboard_analytics.config import Config
from hl_leaderboard_analytics.core import Analytics, FilterSpec, SortKey, Window, write
from hl_leaderboard_analytics.core.mock_data import demo_rows
from hl_leaderboard_analytics.tui.screens import (
    BoardPane, ComparePane, DetailPane, ExportPane, FiltersPane, SettingsPane,
)

_THEMES = ("textual-dark", "nord", "tokyo-night", "solarized-dark")
_SORT_CYCLE = [k.value for k in SortKey]
_WINDOW_CYCLE = [w.value for w in Window]


class LeaderboardApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Hyperliquid Leaderboard Analytics"
    SUB_TITLE = "rank · slice · export — read-only"

    BINDINGS = [
        Binding("1", "tab('board')", "Board", show=False),
        Binding("2", "tab('detail')", "Detail", show=False),
        Binding("3", "tab('filters')", "Filters", show=False),
        Binding("4", "tab('compare')", "Compare", show=False),
        Binding("5", "tab('export')", "Export", show=False),
        Binding("6", "tab('settings')", "Settings", show=False),
        Binding("q", "quit", "Quit"),
        Binding("s", "cycle_sort", "Sort"),
        Binding("w", "cycle_window", "Window"),
        Binding("e", "quick_export", "Export"),
        Binding("t", "cycle_theme", "Theme"),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def __init__(self, config: Config, snapshot=None) -> None:
        super().__init__()
        self.config = config
        self._analytics = Analytics()
        self._spec = FilterSpec(
            window=config.board.default_window,
            sort=config.board.default_sort,
            limit=config.board.page_size,
        )
        self._snapshot = snapshot
        self._focus_index = 0
        self._theme_index = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with TabbedContent(id="tabs", initial="board"):
            yield TabPane("Board", BoardPane(), id="board")
            yield TabPane("Detail", DetailPane(), id="detail")
            yield TabPane("Filters", FiltersPane(), id="filters")
            yield TabPane("Compare", ComparePane(), id="compare")
            yield TabPane("Export", ExportPane(), id="export")
            yield TabPane("Settings", SettingsPane(), id="settings")
        yield Footer()

    def on_mount(self) -> None:  # type: ignore[override]
        self.theme = _THEMES[self._theme_index]
        if self._snapshot is None:
            self._snapshot = self._analytics.snapshot(demo_rows(), self._spec)
        self._push_snapshot(self._snapshot)
        self.query_one(SettingsPane).show(self.config)
        self.query_one(FiltersPane).show(self._spec)

    # --------------------------------------------------------------- data flow

    def _recompute(self) -> None:
        self._snapshot = self._analytics.snapshot(demo_rows(), self._spec)
        self._push_snapshot(self._snapshot)

    def _push_snapshot(self, snapshot) -> None:
        self.query_one(BoardPane).show(snapshot)
        self.query_one(ExportPane).show(snapshot, self.config.export.format)
        if snapshot.rows:
            self.query_one(DetailPane).show(snapshot.rows[self._focus_index])
            self.query_one(ComparePane).show(snapshot.rows[self._focus_index])

    # ----------------------------------------------------------------- actions

    def action_tab(self, pane_id: str) -> None:
        self.query_one(TabbedContent).active = pane_id

    def action_cycle_sort(self) -> None:
        i = _SORT_CYCLE.index(self._spec.sort) if self._spec.sort in _SORT_CYCLE else 0
        self._spec = FilterSpec(
            window=self._spec.window, sort=_SORT_CYCLE[(i + 1) % len(_SORT_CYCLE)],
            asset=self._spec.asset, lev_min=self._spec.lev_min,
            lev_max=self._spec.lev_max, limit=self._spec.limit,
        )
        self._focus_index = 0
        self._recompute()
        self.query_one(FiltersPane).show(self._spec)
        self.notify(f"sort: {self._spec.sort}", timeout=1)

    def action_cycle_window(self) -> None:
        i = _WINDOW_CYCLE.index(self._spec.window) if self._spec.window in _WINDOW_CYCLE else 0
        self._spec = FilterSpec(
            window=_WINDOW_CYCLE[(i + 1) % len(_WINDOW_CYCLE)], sort=self._spec.sort,
            asset=self._spec.asset, lev_min=self._spec.lev_min,
            lev_max=self._spec.lev_max, limit=self._spec.limit,
        )
        self._recompute()
        self.query_one(FiltersPane).show(self._spec)
        self.notify(f"window: {self._spec.window}", timeout=1)

    def action_quick_export(self) -> None:
        fmt = self.config.export.format
        out = write(self._snapshot, Path(self.config.export.out_dir) / f"leaderboard.{fmt}", fmt)
        self.notify(f"exported {len(self._snapshot.rows)} rows → {out}", timeout=3)

    def action_cycle_theme(self) -> None:
        self._theme_index = (self._theme_index + 1) % len(_THEMES)
        self.theme = _THEMES[self._theme_index]
        self.notify(f"theme: {self.theme}", timeout=1)

    def action_help(self) -> None:
        self.notify(
            "1-6 tabs · s sort · w window · e export · t theme · q quit",
            title="Keybindings", timeout=4,
        )
