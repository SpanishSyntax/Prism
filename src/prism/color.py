"""Standardized CLI color arguments, flags, and argv handlers."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from prism.engine import UI


def add_color_args(parser: argparse.ArgumentParser) -> None:
    """
    Adds standardized --color, --no-color, and agent automation flags to an ArgumentParser.
    """
    try:
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
    except argparse.ArgumentError:
        pass

    try:
        parser.add_argument(
            "-A",
            "--agent",
            action="store_true",
            help="Compact agent-friendly output mode (no Unicode boxes, no emojis, no interactive prompts)",
        )
    except argparse.ArgumentError:
        pass

    try:
        parser.add_argument(
            "--json",
            action="store_true",
            help="Structured JSON output for programmatic tool integration",
        )
    except argparse.ArgumentError:
        pass


def handle_color_args(
    argv: Sequence[str] | None = None,
    ui: UI | None = None,
) -> str:
    """
    Scans raw command-line argv for --color, --no-color, and agent flags before full argument
    parsing. This ensures early logging, banner boxes, and --help output honor user color preferences
    and agent mode across all UI instances.

    Returns the resolved color mode: 'auto', 'always', or 'never'.
    """
    from prism.engine import get_all_ui_instances, ui as default_ui
    from prism.styling import check_agent_env, check_json_env

    target_uis = [ui] if ui is not None else get_all_ui_instances()
    if not target_uis:
        target_uis = [default_ui]

    args = argv if argv is not None else sys.argv[1:]
    mode = "auto"
    agent_flag = False
    json_flag = False

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
        elif arg in ("--agent", "-A"):
            agent_flag = True
        elif arg == "--json":
            agent_flag = True
            json_flag = True

    is_json = json_flag or check_json_env()
    is_agent = agent_flag or is_json or check_agent_env()

    for target_ui in target_uis:
        if is_agent:
            target_ui.set_agent_mode(agent=True, json_output=is_json)
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
    from prism.engine import get_all_ui_instances, ui as default_ui

    target_uis = [ui] if ui is not None else get_all_ui_instances()
    if not target_uis:
        target_uis = [default_ui]

    if getattr(args, "no_color", False):
        mode = "never"
    else:
        mode = getattr(args, "color", "auto")

    for target_ui in target_uis:
        target_ui.set_color_mode(mode)
    return mode


def add_agent_args(parser: argparse.ArgumentParser) -> None:
    """
    Adds standardized --agent (-A) and --json flags to an ArgumentParser.
    """
    try:
        parser.add_argument(
            "-A",
            "--agent",
            action="store_true",
            help="Compact agent-friendly output mode (no Unicode boxes, no emojis, no interactive prompts)",
        )
    except argparse.ArgumentError:
        pass

    try:
        parser.add_argument(
            "--json",
            action="store_true",
            help="Structured JSON output for programmatic tool integration",
        )
    except argparse.ArgumentError:
        pass


def handle_agent_args(
    argv: Sequence[str] | None = None,
    ui: UI | None = None,
) -> tuple[bool, bool]:
    """
    Scans raw command-line argv for --agent, -A, --json flags and environment variables.
    Returns (is_agent, is_json).
    """
    from prism.engine import get_all_ui_instances, ui as default_ui
    from prism.styling import check_agent_env, check_json_env

    target_uis = [ui] if ui is not None else get_all_ui_instances()
    if not target_uis:
        target_uis = [default_ui]

    args = argv if argv is not None else sys.argv[1:]

    agent_flag = any(a in ("--agent", "-A") for a in args)
    json_flag = any(a in ("--json",) for a in args)
    env_agent = check_agent_env()
    env_json = check_json_env()

    is_json = json_flag or env_json
    is_agent = agent_flag or is_json or env_agent

    for target_ui in target_uis:
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
    from prism.engine import get_all_ui_instances, ui as default_ui
    from prism.styling import check_agent_env, check_json_env

    target_uis = [ui] if ui is not None else get_all_ui_instances()
    if not target_uis:
        target_uis = [default_ui]

    is_json = getattr(args, "json", False) or check_json_env()
    is_agent = getattr(args, "agent", False) or is_json or check_agent_env()

    for target_ui in target_uis:
        if is_agent:
            target_ui.set_agent_mode(agent=True, json_output=is_json)

    return is_agent, is_json


def handle_version_arg(
    raw_args: Sequence[str],
    version_str: str,
    app_name: str | None = None,
    ui: UI | None = None,
) -> bool:
    """Checks if a version flag (-V, -v, --version, version) was passed in raw_args.

    If matched, outputs the standardized version string/JSON via ui.version() and returns True.
    """
    from prism.engine import get_all_ui_instances, ui as default_ui

    if ui is not None:
        target_ui = ui
    else:
        all_uis = get_all_ui_instances()
        target_ui = all_uis[-1] if all_uis else default_ui

    name = app_name or target_ui.styler.app_name
    is_version = any(a in ("-V", "--version") for a in raw_args) or (
        len(raw_args) == 1 and raw_args[0] in ("-v", "version")
    )
    if is_version:
        target_ui.version(version_str, app_name=name)
        return True
    return False
