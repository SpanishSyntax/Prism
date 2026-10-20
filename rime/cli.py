"""Command line entrypoint and component showcase for Rime."""

from __future__ import annotations

import argparse
import sys
import time

from rime.engine import UI, ui


def run_showcase() -> int:
    """Runs an interactive demonstration showcasing all Rime UI components."""
    ui.panel(
        "RIME CLI DESIGN SYSTEM",
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
            "error: attribute 'rime' missing in pkgs.python3Packages",
            "",
            "       at /etc/nixos/flake.nix:42:15:",
            "          42|   buildInputs = [ pkgs.python3Packages.rime ];",
            "            |                 ^",
        ],
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rime",
        description="Unified, Zero-Dependency CLI Design System & Terminal UI Framework",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run interactive UI component demonstration",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version information",
    )

    args = parser.parse_args(argv)

    if args.version:
        from rime import __version__
        print(f"rime {__version__}")
        return 0

    if args.demo or len(sys.argv) == 1:
        return run_showcase()

    return 0


if __name__ == "__main__":
    sys.exit(main())
