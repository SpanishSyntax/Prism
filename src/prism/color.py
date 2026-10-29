"""Standardized CLI color arguments, flags, and argv handlers."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from prism.engine import UI


def add_color_args(parser: argparse.ArgumentParser) -> None:
    """
    Adds standardized --color and --no-color flags to an ArgumentParser.
    """
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Color output mode: auto, always, never (default: auto)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output (equivalent to --color never)",
    )


def handle_color_args(
    argv: Sequence[str] | None = None,
    ui: UI | None = None,
) -> str:
    """
    Scans raw command-line argv for --color and --no-color flags before full argument
    parsing. This ensures early logging, banner boxes, and --help output honor user color preferences.
    
    Returns the resolved color mode: 'auto', 'always', or 'never'.
    """
    from prism.engine import ui as default_ui

    target_ui = ui if ui is not None else default_ui
    args = argv if argv is not None else sys.argv[1:]
    mode = "auto"

    for i, arg in enumerate(args):
        if arg == "--no-color":
            mode = "never"
        elif arg.startswith("--color="):
            val = arg.split("=", 1)[1].lower()
            if val in ("auto", "always", "never"):
                mode = val
        elif arg == "--color" and i + 1 < len(args):
            val = args[i + 1].lower()
            if val in ("auto", "always", "never"):
                mode = val

    target_ui.set_color_mode(mode)
    return mode


def apply_color_args(
    args: argparse.Namespace,
    ui: UI | None = None,
) -> str:
    """
    Applies parsed arguments (--color and --no-color) to a UI instance.
    Returns the resolved color mode: 'auto', 'always', or 'never'.
    """
    from prism.engine import ui as default_ui

    target_ui = ui if ui is not None else default_ui
    if getattr(args, "no_color", False):
        mode = "never"
    else:
        mode = getattr(args, "color", "auto")

    target_ui.set_color_mode(mode)
    return mode


def add_agent_args(parser: argparse.ArgumentParser) -> None:
    """
    Adds standardized --agent (-A) and --json flags to an ArgumentParser.
    """
    parser.add_argument(
        "-A",
        "--agent",
        action="store_true",
        help="Compact agent-friendly output mode (no Unicode boxes, no emojis, no interactive prompts)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Structured JSON output for programmatic tool integration",
    )


def handle_agent_args(
    argv: Sequence[str] | None = None,
    ui: UI | None = None,
) -> tuple[bool, bool]:
    """
    Scans raw command-line argv for --agent, -A, --json flags and environment variables.
    Returns (is_agent, is_json).
    """
    from prism.engine import ui as default_ui
    from prism.styling import check_agent_env

    target_ui = ui if ui is not None else default_ui
    args = argv if argv is not None else sys.argv[1:]

    agent_flag = any(a in ("--agent", "-A") for a in args)
    json_flag = any(a in ("--json",) for a in args)
    env_agent = check_agent_env()

    is_agent = agent_flag or json_flag or env_agent
    is_json = json_flag

    if is_agent:
        target_ui.set_agent_mode(agent=True, json_output=is_json)

    return is_agent, is_json


def apply_agent_args(
    args: argparse.Namespace,
    ui: UI | None = None,
) -> tuple[bool, bool]:
    """
    Applies parsed arguments (--agent and --json) to a UI instance.
    """
    from prism.engine import ui as default_ui
    from prism.styling import check_agent_env

    target_ui = ui if ui is not None else default_ui
    is_agent = getattr(args, "agent", False) or getattr(args, "json", False) or check_agent_env()
    is_json = getattr(args, "json", False)

    if is_agent:
        target_ui.set_agent_mode(agent=True, json_output=is_json)

    return is_agent, is_json
