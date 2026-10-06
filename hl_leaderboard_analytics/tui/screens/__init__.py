"""Tab panes for the leaderboard dashboard."""

from hl_leaderboard_analytics.tui.screens.board import BoardPane
from hl_leaderboard_analytics.tui.screens.compare import ComparePane
from hl_leaderboard_analytics.tui.screens.detail import DetailPane
from hl_leaderboard_analytics.tui.screens.export_pane import ExportPane
from hl_leaderboard_analytics.tui.screens.filters import FiltersPane
from hl_leaderboard_analytics.tui.screens.settings import SettingsPane

__all__ = ["BoardPane", "ComparePane", "DetailPane", "ExportPane", "FiltersPane", "SettingsPane"]
