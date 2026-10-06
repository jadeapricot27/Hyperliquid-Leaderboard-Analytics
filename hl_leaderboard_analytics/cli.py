"""CLI entry point: launches the TUI, or exports a view and exits."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from hl_leaderboard_analytics import __version__
from hl_leaderboard_analytics.config import Config, default_config_path
from hl_leaderboard_analytics.core import Analytics, FilterSpec, write
from hl_leaderboard_analytics.core.mock_data import demo_rows


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hl-leaderboard",
        description="Terminal analytics dashboard for the Hyperliquid leaderboard.",
    )
    p.add_argument("--version", "-V", action="version", version=f"hl-leaderboard {__version__}")
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--sort", default=None, help="roi|volume|win_rate|sharpe|profit_factor|drawdown")
    p.add_argument("--window", default=None, help="7d|30d|90d|all")
    p.add_argument("--asset", default=None, help="e.g. BTC-PERP")
    p.add_argument("--lev", default=None, help="leverage band, e.g. 5-20")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--export", type=Path, default=None, help="write a view and exit")
    p.add_argument("--format", default=None, help="csv|json|markdown (with --export)")
    return p


def _parse_lev(spec: str) -> tuple[float, float]:
    if "-" in spec:
        lo, hi = spec.split("-", 1)
        return float(lo), float(hi)
    v = float(spec)
    return v, 1000.0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    demo = args.demo or os.environ.get("HL_LEADERBOARD_DEMO", "") == "1"
    config = Config.load(args.config or Path(os.environ.get("HL_LEADERBOARD_CONFIG",
                                                            str(default_config_path()))), demo=demo)

    lev_min, lev_max = (0.0, 1000.0)
    if args.lev:
        lev_min, lev_max = _parse_lev(args.lev)

    spec = FilterSpec(
        window=args.window or config.board.default_window,
        sort=args.sort or config.board.default_sort,
        asset=args.asset or "",
        lev_min=lev_min,
        lev_max=lev_max,
        limit=args.limit if args.limit is not None else config.board.page_size,
    )

    snapshot = Analytics().snapshot(demo_rows(), spec)

    if args.export:
        fmt = args.format or config.export.format
        out = write(snapshot, args.export, fmt)
        print(f"exported {len(snapshot.rows)} rows → {out} ({fmt})", file=sys.stderr)
        return 0

    try:
        from hl_leaderboard_analytics.tui.app import LeaderboardApp
    except ImportError as exc:  # pragma: no cover
        print(f"error: TUI deps missing ({exc}). Run `pip install -e .`.", file=sys.stderr)
        return 2

    LeaderboardApp(config=config, snapshot=snapshot).run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
