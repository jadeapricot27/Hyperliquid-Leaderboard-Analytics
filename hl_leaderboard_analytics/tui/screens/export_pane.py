"""Export pane — preview of the exportable payload + format hint."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from hl_leaderboard_analytics.core.models import BoardSnapshot
from hl_leaderboard_analytics.core.export import to_csv, to_json, to_markdown


class ExportPane(Vertical):
    DEFAULT_CSS = """
    ExportPane { padding: 1 2; }
    ExportPane Static#export-preview { margin-top: 1; padding: 1 1; border: round $panel; }
    """

    def show(self, snapshot: BoardSnapshot, fmt: str = "csv") -> None:
        preview_map = {"csv": to_csv, "json": to_json, "markdown": to_markdown}
        text = preview_map.get(fmt, to_csv)(snapshot)
        head = "\n".join(text.splitlines()[:8])
        more = "" if len(text.splitlines()) <= 8 else f"\n[dim]… {len(text.splitlines()) - 8} more lines[/]"
        self.query_one("#export-preview", Static).update(
            f"[bold]Format:[/] {fmt}   [bold]Rows:[/] {len(snapshot.rows)}\n\n"
            f"[dim]── preview (head) ──[/]\n{head}{more}\n\n"
            "[dim]Press [/][bold]e[/][dim] to write the full export to the configured out_dir, "
            "or run `hl-leaderboard --export out.{ext}` from the shell.[/]"
        )

    def compose(self) -> ComposeResult:
        yield Static("📤  EXPORT", classes="pane-title")
        yield Static(id="export-preview")
