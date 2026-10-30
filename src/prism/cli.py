"""Command line entrypoint and component showcase for Prism."""

from __future__ import annotations

import argparse
import sys
import time

from prism import __version__
from prism.color import add_color_args, handle_color_args
from prism.engine import UI, ui


def run_showcase() -> int:
    """Runs an interactive demonstration showcasing all Prism UI components."""
    ui.panel(
        "PRISM CLI DESIGN SYSTEM",
        [
            ui.bold_cyan("Unified Terminal UI Framework for Frost Icebergs"),
            ui.dim("Zero dependencies • ANSI styling • Bounding boxes • Spinners • Menus"),
            "",
            f"  {ui.cyan('• Badges:')}  {ui.badge()}  ❄️ [folio]  🌌 [borealis]  🧊 [cryo]  ✨ [glaze]",
            f"  {ui.cyan('• Colors:')}  {ui.bold_green('success')} {ui.bold_cyan('action')} {ui.yellow('warning')} {ui.red('error')}",
        ],
        border_color="1;36",
    )

    print()
    ui.info("Demonstrating logging primitives:")
    ui.action("Dispatched compilation job to daemon", symbol="🚀")
    ui.success("Finished building derivations successfully")
    ui.warn("Nix flake lockfile is older than 30 days")
    ui.error("Subprocess terminated with exit code 1")

    print()
    ui.subheader("Spinner Demonstration")
    with ui.spinner("Resolving flake inputs and downloading closures..."):
        time.sleep(1.0)
    ui.success("Closure graph materialized")

    print()
    ui.subheader("Diagnostic Error Box")
    ui.error_panel(
        "Evaluation Failed",
        [
            "error: attribute 'prism' missing in pkgs.python3Packages",
            "",
            "       at /etc/nixos/flake.nix:42:15:",
            "          42|   buildInputs = [ pkgs.python3Packages.prism ];",
            "            |                 ^",
        ],
    )
    return 0


def print_help() -> None:
    """Prints usage help for Prism CLI."""
    if ui.is_agent:
        print(f"""Prism v{__version__} - Unified CLI Design System & Terminal UI Framework
Usage: prism [options]

Options:
  -A, --agent            Compact machine/agent friendly output mode
  --json                 Structured JSON output mode
  --demo                 Run interactive UI component demonstration
  --color MODE           Color output mode: auto, always, never
  --no-color             Disable colored output
  -V, -v, --version      Show version information and exit
  -h, --help             Show this help message and exit
""")
        return

    print(f"""{ui.badge()} {ui.bold("Unified, Zero-Dependency CLI Design System & Terminal UI Framework")}

{ui.blue("Usage:")}
  prism [options]

{ui.blue("Options:")}
  --demo                 Run interactive UI component demonstration
  -A, --agent            Compact machine/agent friendly output mode
  --json                 Structured JSON output mode
  --color MODE           Color output mode: auto, always, never (default: auto)
  --no-color             Disable colored output
  -V, -v, --version      Show version information and exit
  -h, --help             Show this help message and exit
""")


def main(argv: list[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    handle_color_args(raw_args)

    if any(a in ("-h", "--help", "help") for a in raw_args):
        print_help()
        return 0

    if ui.handle_version_arg(raw_args, __version__):
        return 0

    parser = argparse.ArgumentParser(
        prog="prism",
        description="Unified, Zero-Dependency CLI Design System & Terminal UI Framework",
        add_help=False,
    )
    add_color_args(parser)
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run interactive UI component demonstration",
    )
    parser.add_argument(
        "-V",
        "-v",
        "--version",
        action="store_true",
        help="Print version information",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="Show help message",
    )

    args = parser.parse_args(raw_args)

    if args.version:
        ui.version(__version__)
        return 0

    if args.demo or (len(raw_args) == 0 and ui.is_interactive):
        return run_showcase()

    if len(raw_args) == 0 and not ui.is_interactive:
        if ui.is_json:
            ui.json({"status": "ok", "app": "prism", "version": __version__})
            return 0
        print_help()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
