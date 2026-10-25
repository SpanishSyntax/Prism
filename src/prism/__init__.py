"""Prism: Unified, Zero-Dependency CLI Design System & Terminal UI Framework."""

from __future__ import annotations

from prism.color import add_color_args, apply_color_args, handle_color_args
from prism.engine import UI, ui
from prism.inputs import confirm_input, prompt_input
from prism.menus import multiselect_menu, select_menu
from prism.panels import render_error_panel, render_panel
from prism.spinner import Spinner, spinner_context
from prism.styling import Styler, detect_color_support
from prism.terminal import (
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
