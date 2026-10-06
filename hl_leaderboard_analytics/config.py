"""Configuration loader."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
    _LOAD = tomllib.loads
else:  # pragma: no cover
    import tomli as _tomli
    _LOAD = _tomli.loads


def default_config_path() -> Path:
    from platformdirs import user_config_dir
    return Path(user_config_dir("hl-leaderboard", appauthor=False)) / "config.toml"


DEFAULT_TOML = """\
[network]
api_url = "https://api.hyperliquid.xyz"
timeout_seconds = 10
max_rps = 5

[board]
default_window = "90d"
default_sort = "roi"
page_size = 100
show_aliases = true

[export]
format = "csv"
out_dir = "./exports"
"""


@dataclass(frozen=True)
class NetworkConfig:
    api_url: str = "https://api.hyperliquid.xyz"
    timeout_seconds: int = 10
    max_rps: int = 5


@dataclass(frozen=True)
class BoardConfig:
    default_window: str = "90d"
    default_sort: str = "roi"
    page_size: int = 100
    show_aliases: bool = True


@dataclass(frozen=True)
class ExportConfig:
    format: str = "csv"
    out_dir: str = "./exports"


@dataclass(frozen=True)
class Config:
    network: NetworkConfig = field(default_factory=NetworkConfig)
    board: BoardConfig = field(default_factory=BoardConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    demo: bool = False

    @classmethod
    def load(cls, path: Path, *, demo: bool = False) -> Config:
        path = Path(path)
        if not path.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(DEFAULT_TOML, encoding="utf-8")
            except OSError:
                pass
        raw = _LOAD(path.read_text(encoding="utf-8")) if path.exists() else {}
        return cls(
            network=NetworkConfig(**raw.get("network", {})),
            board=BoardConfig(**raw.get("board", {})),
            export=ExportConfig(**raw.get("export", {})),
            demo=demo,
        )
