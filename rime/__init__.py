"""Rime: Unified, Zero-Dependency CLI Design System & Terminal UI Framework."""

from __future__ import annotations

from rime.color import add_color_args, apply_color_args, handle_color_args
from rime.engine import UI, ui
from rime.inputs import confirm_input, prompt_input
from rime.menus import multiselect_menu, select_menu
from rime.panels import render_error_panel, render_panel
from rime.spinner import Spinner, spinner_context
from rime.styling import Styler, detect_color_support
from rime.terminal import (
    cbreak_mode,
    get_key,
    get_terminal_columns,
    get_terminal_size,
    read_key,
    strip_ansi,
    visual_len,
)

__version__ = "0.1.0"

__all__ = [
    "UI",
    "ui",
    "add_color_args",
    "handle_color_args",
    "apply_color_args",
    "Styler",
    "Spinner",
    "spinner_context",
    "detect_color_support",
    "render_panel",
    "render_error_panel",
    "prompt_input",
    "confirm_input",
    "select_menu",
    "multiselect_menu",
    "read_key",
    "get_key",
    "cbreak_mode",
    "strip_ansi",
    "visual_len",
    "get_terminal_columns",
    "get_terminal_size",
]
