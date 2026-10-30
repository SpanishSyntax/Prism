"""Prism: Unified, Zero-Dependency CLI Design System & Terminal UI Framework."""

from __future__ import annotations

from prism.color import (
    add_agent_args,
    add_color_args,
    apply_agent_args,
    apply_color_args,
    handle_agent_args,
    handle_color_args,
    handle_version_arg,
)
from prism.engine import UI, ui
from prism.help import HelpBuilder, render_help
from prism.inputs import confirm_input, prompt_input
from prism.menus import multiselect_menu, select_menu
from prism.panels import render_error_panel, render_panel
from prism.spinner import Spinner, spinner_context
from prism.styling import (
    Styler,
    check_agent_env,
    check_json_env,
    check_toon_env,
    detect_color_support,
    get_agent_env,
    get_json_env,
    get_toon_env,
)
from prism.terminal import (
    cbreak_mode,
    get_key,
    get_terminal_columns,
    get_terminal_size,
    read_key,
    strip_ansi,
    strip_emojis,
    visual_len,
)
from prism.toon import encode_toon, format_scalar

__version__ = "0.1.0"

__all__ = [
    "UI",
    "ui",
    "add_color_args",
    "handle_color_args",
    "apply_color_args",
    "add_agent_args",
    "handle_agent_args",
    "apply_agent_args",
    "check_agent_env",
    "check_json_env",
    "check_toon_env",
    "get_agent_env",
    "get_json_env",
    "get_toon_env",
    "encode_toon",
    "format_scalar",
    "handle_version_arg",
    "HelpBuilder",
    "render_help",
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
    "strip_emojis",
    "visual_len",
    "get_terminal_columns",
    "get_terminal_size",
]
