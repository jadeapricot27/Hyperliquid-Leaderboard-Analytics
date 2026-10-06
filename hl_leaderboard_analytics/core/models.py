"""Typed data models for the leaderboard analytics engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Window(str, Enum):
    D7 = "7d"
    D30 = "30d"
    D90 = "90d"
    ALL = "all"


class SortKey(str, Enum):
    ROI = "roi"
    VOLUME = "volume"
    WIN_RATE = "win_rate"
    SHARPE = "sharpe"
    PROFIT_FACTOR = "profit_factor"
    DRAWDOWN = "drawdown"


@dataclass(frozen=True)
class WindowStats:
    """Aggregated stats for one time window."""

    roi: float
    volume: float
    win_rate: float
    sharpe: float
    profit_factor: float
    max_drawdown: float
    trades: int


@dataclass(frozen=True)
class AssetPnl:
    symbol: str
    pnl_usd: float
    share: float          # share of total abs PnL, 0..1


@dataclass(frozen=True)
class LeaderboardRow:
    """One row of the (filtered, sorted) board."""

    rank: int
    alias: str
    address: str
    windows: dict[str, WindowStats]      # keyed by Window value
    leverage: float                       # representative avg leverage
    side_bias: float                      # −1 (short) .. +1 (long)
    top_assets: list[AssetPnl]

    @property
    def short(self) -> str:
        return f"{self.address[:6]}…{self.address[-4:]}" if len(self.address) >= 12 else self.address

    def stat(self, window: str, key: str) -> float:
        w = self.windows.get(window)
        if w is None:
            return 0.0
        return float(getattr(w, key))


@dataclass(frozen=True)
class FilterSpec:
    window: str = "90d"
    sort: str = "roi"
    asset: str = ""          # "" = all
    lev_min: float = 0.0
    lev_max: float = 1000.0
    limit: int = 100


@dataclass(frozen=True)
class MoverRecord:
    alias: str
    address: str
    delta_24h: float         # fractional change in equity over 24h
    direction: str           # "up" | "down"


@dataclass(frozen=True)
class BoardSnapshot:
    """The full result of an analytics pass: rows + computed extras."""

    rows: list[LeaderboardRow]
    movers: list[MoverRecord] = field(default_factory=list)
    filter: FilterSpec = field(default_factory=FilterSpec)
    total_traders: int = 0
