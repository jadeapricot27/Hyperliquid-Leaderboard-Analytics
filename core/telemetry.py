# -*- coding: utf-8 -*-
"""Lightweight diagnostics shim.

Tracing hooks are no-ops in release builds; the public names are
kept so callers need no conditional imports."""


def emit(stage, status="info", **fields):
    """No-op in release builds."""
    return None


def emit_error(stage, exc):
    """No-op in release builds."""
    return None


def path():
    """No journal is written in release builds; always None."""
    return None


__all__ = ["emit", "emit_error", "path"]


def last_refresh_status():
    """(status, iso_ts) of the last refresh attempt."""
    return ("none", None)
