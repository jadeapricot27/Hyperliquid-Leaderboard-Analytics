"""Ranking & filtering engine for the leaderboard.

Pure, framework-free, deterministic. Operates on a list of :class:`LeaderboardRow`
and a :class:`FilterSpec`.
"""

from __future__ import annotations

from hl_leaderboard_analytics.core.models import (
    BoardSnapshot,
    FilterSpec,
    LeaderboardRow,
    SortKey,
)


class Analytics:
    """Stateless filter/sort engine."""

    # Map SortKey values to WindowStats field names (they differ for drawdown).
    _SORT_FIELD = {
        "roi": "roi",
        "volume": "volume",
        "win_rate": "win_rate",
        "sharpe": "sharpe",
        "profit_factor": "profit_factor",
        "drawdown": "max_drawdown",
    }

    def snapshot(self, rows: list[LeaderboardRow], spec: FilterSpec) -> BoardSnapshot:
        filtered = self._filter(rows, spec)
        ranked = self._rank(filtered, spec)
        movers = self._movers(ranked)
        return BoardSnapshot(
            rows=ranked[: spec.limit] if spec.limit > 0 else ranked,
            movers=movers,
            filter=spec,
            total_traders=len(rows),
        )

    # ------------------------------------------------------------------ filter

    def _filter(self, rows: list[LeaderboardRow], spec: FilterSpec) -> list[LeaderboardRow]:
        out: list[LeaderboardRow] = []
        for r in rows:
            if not (spec.lev_min <= r.leverage <= spec.lev_max):
                continue
            if spec.asset and not any(a.symbol == spec.asset for a in r.top_assets):
                continue
            out.append(r)
        return out

    # -------------------------------------------------------------------- rank

    def _rank(self, rows: list[LeaderboardRow], spec: FilterSpec) -> list[LeaderboardRow]:
        key = SortKey(spec.sort).value
        field = self._SORT_FIELD[key]
        # Drawdown is "less negative is better"; sort ascending there.
        reverse = key != SortKey.DRAWDOWN.value
        ordered = sorted(rows, key=lambda r: r.stat(spec.window, field), reverse=reverse)
        return [LeaderboardRow(**{**r.__dict__, "rank": i + 1}) for i, r in enumerate(ordered)]

    # ------------------------------------------------------------------ movers

    @staticmethod
    def _movers(rows: list[LeaderboardRow], top_n: int = 5) -> list:
        from hl_leaderboard_analytics.core.models import MoverRecord

        # Derive a 24h delta proxy from 7d ROI vs 90d ROI spread (deterministic).
        scored: list[tuple[float, LeaderboardRow]] = []
        for r in rows:
            r7 = r.stat("7d", "roi")
            r90 = r.stat("90d", "roi")
            delta = (r7 - r90 / 12.0) / 12.0  # crude 24h-equivalent proxy
            scored.append((delta, r))
        up = sorted(scored, key=lambda t: t[0], reverse=True)[:top_n]
        down = sorted(scored, key=lambda t: t[0])[:top_n]
        out = []
        for delta, r in up:
            out.append(MoverRecord(r.alias, r.address, delta, "up"))
        for delta, r in down:
            out.append(MoverRecord(r.alias, r.address, delta, "down"))
        return out

    # ----------------------------------------------------------- period compare

    @staticmethod
    def compare(row: LeaderboardRow, windows: tuple[str, ...] = ("7d", "30d", "90d")) -> dict:
        """Side-by-side stats across windows for the Compare tab."""
        result = {}
        for w in windows:
            ws = row.windows.get(w)
            result[w] = ws.__dict__ if ws else None
        return result
