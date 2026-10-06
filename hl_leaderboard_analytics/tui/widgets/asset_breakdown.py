"""A Static that renders a trader's per-asset PnL breakdown as a bar-ish list."""

from __future__ import annotations

from textual.widgets import Static

from hl_leaderboard_analytics.core.models import AssetPnl


class AssetBreakdown(Static):
    """Renders ``symbol  $pnl  share ████████`` per asset."""

    def show(self, assets: list[AssetPnl]) -> None:
        if not assets:
            self.update("[dim]no asset data[/]")
            return
        total_share = sum(a.share for a in assets) or 1.0
        lines: list[str] = []
        for a in sorted(assets, key=lambda x: x.share, reverse=True):
            bars = "█" * max(1, int(round(a.share / total_share * 20)))
            lines.append(
                f"[bold]{a.symbol:12}[/] [green]{a.pnl_usd / 1e6:6.2f}M[/]  "
                f"[dim]{a.share * 100:4.0f}%[/] [cyan]{bars}[/]"
            )
        self.update("\n".join(lines))
