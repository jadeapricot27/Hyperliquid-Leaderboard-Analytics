"""Deterministic demo dataset for ``--demo`` mode (no network access)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from hl_leaderboard_analytics.core.models import (
    AssetPnl,
    LeaderboardRow,
    MoverRecord,
    WindowStats,
)

_NOW = datetime(2026, 7, 19, 14, 2, tzinfo=timezone.utc)

# (alias, address, leverage, side_bias, {(window): (roi, volume, win, sharpe, pf, dd, trades), [asset pnls])
_PERSONAS = [
    ("quant_kappa", "0x7f3a91c4e1aabb02d774e9f0c5d8a1b3e6f9c4e1", 5.0, 0.40,
     {"7d": (0.582, 0.42e6, 0.69, 1.95, 2.31, -0.061, 142),
      "30d": (0.182, 1.61e6, 0.70, 1.90, 2.61, -0.104, 612),
      "90d": (4.128, 4.81e6, 0.713, 1.82, 2.84, -0.312, 1284),
      "all": (11.4, 18.2e6, 0.72, 1.88, 2.72, -0.41, 5102)},
     [("BTC-PERP", 2.9e6, 0.48), ("ETH-PERP", 1.4e6, 0.23), ("SOL-PERP", 0.51e6, 0.29)]),
    ("leverage_ape", "0xab24de0f7781cc5529b34f10a98c7d2e5b8a1033", 20.0, 0.15,
     {"7d": (2.124, 1.30e6, 0.49, 0.71, 1.21, -0.31, 88),
      "30d": (0.94, 4.4e6, 0.50, 0.68, 1.27, -0.45, 301),
      "90d": (12.74, 9.30e6, 0.521, 0.74, 1.38, -0.612, 412),
      "all": (28.1, 31.0e6, 0.53, 0.80, 1.42, -0.78, 1402)},
     [("HYPE-PERP", 5.1e6, 0.55), ("BTC-PERP", 2.2e6, 0.24), ("KASPA-PERP", 2.0e6, 0.21)]),
    ("steady_basis", "0xc0ffee15dec0ffee15dec0ffee15dec0ffee15de", 2.0, -0.05,
     {"7d": (0.113, 0.09e6, 0.74, 2.80, 2.51, -0.012, 71),
      "30d": (0.041, 0.39e6, 0.73, 2.78, 2.44, -0.021, 280),
      "90d": (0.84, 1.22e6, 0.731, 2.73, 2.41, -0.082, 2103),
      "all": (2.9, 4.8e6, 0.74, 2.75, 2.38, -0.12, 8800)},
     [("ETH-PERP", 0.7e6, 0.58), ("BTC-PERP", 0.5e6, 0.42)]),
    ("delta_neutral", "0x1b3e6f9c4e1aabb02d774e9f0c5d8a1b3e6f9c4e", 4.0, 0.02,
     {"7d": (0.068, 0.21e6, 0.68, 2.12, 2.05, -0.018, 64),
      "30d": (0.024, 0.78e6, 0.68, 2.10, 2.01, -0.030, 254),
      "90d": (0.614, 2.04e6, 0.68, 2.10, 2.08, -0.071, 980),
      "all": (1.8, 7.6e6, 0.69, 2.11, 2.04, -0.10, 3900)},
     [("BTC-PERP", 1.3e6, 0.64), ("ETH-PERP", 0.74e6, 0.36)]),
    ("basis_hunter", "0x4422aabbccdd00112233445566778899aabbcc00", 3.0, 0.30,
     {"7d": (0.091, 0.08e6, 0.65, 1.98, 1.95, -0.024, 58),
      "30d": (0.032, 0.31e6, 0.64, 1.95, 1.90, -0.040, 230),
      "90d": (0.472, 0.88e6, 0.645, 1.95, 1.92, -0.094, 870),
      "all": (1.4, 3.1e6, 0.65, 1.96, 1.88, -0.14, 3400)},
     [("SOL-PERP", 0.42e6, 0.48), ("BTC-PERP", 0.46e6, 0.52)]),
]


def demo_rows() -> list[LeaderboardRow]:
    out: list[LeaderboardRow] = []
    for alias, address, lev, bias, wins, assets in _PERSONAS:
        windows = {
            w: WindowStats(roi=r, volume=v, win_rate=wr, sharpe=s, profit_factor=pf,
                           max_drawdown=dd, trades=t)
            for w, (r, v, wr, s, pf, dd, t) in wins.items()
        }
        out.append(LeaderboardRow(
            rank=0, alias=alias, address=address, windows=windows,
            leverage=lev, side_bias=bias,
            top_assets=[AssetPnl(symbol=s, pnl_usd=p, share=sh) for s, p, sh in assets],
        ))
    return out


def equity_curve(row: LeaderboardRow, points: int = 80) -> list[float]:
    w = row.windows.get("90d") or row.windows.get("30d") or row.windows.get("7d")
    target = 1.0 + (w.roi if w else 0.5)
    if points <= 1:
        return [target]
    span = points - 1
    return [1.0 + (target - 1.0) * (i / span) ** 1.25 + 0.012 * math.sin(i / 5.0) * (1 - i / span)
            for i in range(points)]


def demo_movers(rows: list[LeaderboardRow]) -> list[MoverRecord]:
    out: list[MoverRecord] = []
    for r in rows:
        r7 = r.stat("7d", "roi")
        r90 = r.stat("90d", "roi")
        delta = (r7 - r90 / 12.0) / 12.0
        out.append(MoverRecord(r.alias, r.address, delta, "up" if delta >= 0 else "down"))
    return out


def demo_now() -> datetime:
    return _NOW
