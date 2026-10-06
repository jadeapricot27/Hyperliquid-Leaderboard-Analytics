"""Export writers: CSV / JSON / Markdown."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from hl_leaderboard_analytics.core.models import BoardSnapshot, FilterSpec


def _row_dict(snapshot: BoardSnapshot, row_idx: int) -> dict[str, object]:
    row = snapshot.rows[row_idx]
    w = row.windows.get(snapshot.filter.window)
    base = {
        "rank": row.rank,
        "alias": row.alias,
        "address": row.address,
        "leverage": round(row.leverage, 2),
        "side_bias": round(row.side_bias, 2),
    }
    if w is not None:
        base.update({
            "roi": round(w.roi, 4),
            "volume": round(w.volume, 2),
            "win_rate": round(w.win_rate, 4),
            "sharpe": round(w.sharpe, 4),
            "profit_factor": round(w.profit_factor, 4),
            "max_drawdown": round(w.max_drawdown, 4),
            "trades": w.trades,
        })
    return base


def to_csv(snapshot: BoardSnapshot) -> str:
    if not snapshot.rows:
        return ""
    buf = io.StringIO()
    fieldnames = list(_row_dict(snapshot, 0).keys())
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(snapshot.rows)):
        writer.writerow(_row_dict(snapshot, i))
    return buf.getvalue()


def to_json(snapshot: BoardSnapshot) -> str:
    return json.dumps(
        {
            "filter": snapshot.filter.__dict__,
            "total_traders": snapshot.total_traders,
            "rows": [_row_dict(snapshot, i) for i in range(len(snapshot.rows))],
        },
        indent=2,
    )


def to_markdown(snapshot: BoardSnapshot) -> str:
    if not snapshot.rows:
        return "_no rows_"
    keys = list(_row_dict(snapshot, 0).keys())
    lines = ["| " + " | ".join(keys) + " |", "|" + "|".join(["---"] * len(keys)) + "|"]
    for i in range(len(snapshot.rows)):
        lines.append("| " + " | ".join(str(_row_dict(snapshot, i)[k]) for k in keys) + " |")
    return "\n".join(lines)


def write(snapshot: BoardSnapshot, path: Path, fmt: str) -> Path:
    fmt = fmt.lower()
    payload = {"csv": to_csv, "json": to_json, "markdown": to_markdown}.get(fmt, to_csv)(snapshot)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return path
