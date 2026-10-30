"""ANSI color formatting, styling primitives, and status badge generator."""

from __future__ import annotations

import json
import os
import sys
from typing import Any, TextIO

from prism.terminal import strip_ansi, strip_emojis


def check_agent_env() -> bool:
    """Checks environment variables for global Iceberg agent automation mode."""
    for var in (
        "ICEBERG_AGENT_MODE",
        "PRISM_AGENT_MODE",
        "AGENT_MODE",
        "LANTERN_AGENT_MODE",
        "ICEBERG_JSON_MODE",
        "PRISM_JSON_MODE",
        "JSON_MODE",
    ):
        val = os.environ.get(var, "").lower()
        if val in ("1", "true", "yes", "on"):
            return True
    return False


def check_json_env() -> bool:
    """Checks environment variables for global Iceberg JSON output mode."""
    for var in ("ICEBERG_JSON_MODE", "PRISM_JSON_MODE", "JSON_MODE"):
        val = os.environ.get(var, "").lower()
        if val in ("1", "true", "yes", "on"):
            return True
    return False


def get_agent_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Returns environment dictionary enabling agent automation mode across all child processes.

    Sets ICEBERG_AGENT_MODE=1, PRISM_AGENT_MODE=1, and AGENT_MODE=1.
    """
    env = {
        "ICEBERG_AGENT_MODE": "1",
        "PRISM_AGENT_MODE": "1",
        "AGENT_MODE": "1",
    }
    if extra:
        env.update(extra)
    return env


def get_json_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Returns environment dictionary enabling JSON output mode across all child processes.

    Sets ICEBERG_JSON_MODE=1, PRISM_JSON_MODE=1, JSON_MODE=1, and ICEBERG_AGENT_MODE=1.
    """
    env = {
        "ICEBERG_AGENT_MODE": "1",
        "PRISM_AGENT_MODE": "1",
        "AGENT_MODE": "1",
        "ICEBERG_JSON_MODE": "1",
        "PRISM_JSON_MODE": "1",
        "JSON_MODE": "1",
    }
    if extra:
        env.update(extra)
    return env


def detect_color_support(mode: str = "auto", stream: TextIO | None = None) -> bool:
    """Determines if the output stream supports ANSI color codes."""
    m = mode.lower()
    if m == "never":
        return False
    if m == "always":
        return True
    if "NO_COLOR" in os.environ:
        return False
    if os.environ.get("CLICOLOR_FORCE", "0") != "0" or "FORCE_COLOR" in os.environ:
        return True

    target = stream or sys.stdout
    if hasattr(target, "isatty") and target.isatty():
        return True
    return os.environ.get("COLORTERM") in ("truecolor", "24bit")


class Styler:
    """Configurable ANSI color, badge, and text style generator."""

    def __init__(
        self,
        app_name: str = "prism",
        icon: str = "🌈",
        badge_color: str = "1;36",
        color_mode: str = "auto",
        stream: TextIO | None = None,
        agent_mode: bool | None = None,
    ) -> None:
        self.app_name = app_name
        self.icon = icon
        self.badge_color = badge_color
        self._color_mode = color_mode
        self._stream = stream
        self._agent_mode = check_agent_env() if agent_mode is None else agent_mode
        self._json_mode = False

    @property
    def stream(self) -> TextIO:
        return self._stream if self._stream is not None else sys.stdout

    def set_stream(self, stream: TextIO) -> None:
        self._stream = stream

    def set_color_mode(self, mode: str) -> None:
        self._color_mode = mode.lower()

    def set_agent_mode(self, agent: bool = True, json_output: bool = False) -> None:
        """Sets agent / AI automation mode."""
        self._agent_mode = agent
        self._json_mode = json_output

    @property
    def is_agent(self) -> bool:
        return self._agent_mode

    @property
    def is_json(self) -> bool:
        return self._json_mode

    @property
    def is_interactive(self) -> bool:
        """True only when stdin is an interactive TTY and neither agent nor JSON mode is active."""
        if self._agent_mode or self._json_mode:
            return False
        return bool(hasattr(sys.stdin, "isatty") and sys.stdin.isatty())

    @property
    def use_color(self) -> bool:
        if self._agent_mode and self._color_mode != "always":
            return False
        return detect_color_support(self._color_mode, self.stream)

    def style(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.use_color else text

    def bold(self, text: str) -> str:
        return self.style(text, "1")

    def dim(self, text: str) -> str:
        return self.style(text, "90")

    def italic(self, text: str) -> str:
        return self.style(text, "3")

    def underline(self, text: str) -> str:
        return self.style(text, "4")

    def blue(self, text: str) -> str:
        return self.style(text, "1;34")

    def cyan(self, text: str) -> str:
        return self.style(text, "0;36")

    def bold_cyan(self, text: str) -> str:
        return self.style(text, "1;36")

    def green(self, text: str) -> str:
        return self.style(text, "0;32")

    def bold_green(self, text: str) -> str:
        return self.style(text, "1;32")

    def yellow(self, text: str) -> str:
        return self.style(text, "1;33")

    def red(self, text: str) -> str:
        return self.style(text, "1;31")

    def magenta(self, text: str) -> str:
        return self.style(text, "1;35")

    def badge(self) -> str:
        if self._agent_mode:
            return f"[{self.app_name}]"
        return self.style(f"{self.icon} [{self.app_name}]", self.badge_color)

    def status(self, symbol: str, message: str, code: str = "1") -> str:
        if self._agent_mode:
            return f"{self.badge()} {message}"
        return f"{self.badge()} {self.style(f'{symbol} {message}', code)}"

    def success(self, msg: str) -> None:
        if self._json_mode:
            return
        if self._agent_mode:
            print(f"{self.badge()} [ok] {msg}", file=self.stream)
            return
        print(self.status("✔", msg, "1;32"), file=self.stream)

    def info(self, msg: str, symbol: str = "ℹ️") -> None:
        if self._json_mode:
            return
        if self._agent_mode:
            print(f"{self.badge()} {msg}", file=self.stream)
            return
        print(self.status(symbol, msg, "1;34"), file=self.stream)

    def warn(self, msg: str) -> None:
        if self._json_mode:
            return
        if self._agent_mode:
            print(f"{self.badge()} [warn] {msg}", file=self.stream)
            return
        print(self.status("⚠️", msg, "1;33"), file=self.stream)

    def error(self, msg: str) -> None:
        if self._json_mode:
            print(json.dumps({"status": "error", "error": strip_ansi(msg)}), file=sys.stderr)
            return
        if self._agent_mode:
            print(f"{self.badge()} [error] {msg}", file=sys.stderr)
            return
        print(self.status("✘", msg, "1;31"), file=sys.stderr)

    def action(self, msg: str, symbol: str = "⚡") -> None:
        if self._json_mode:
            return
        if self._agent_mode:
            print(f"{self.badge()} {msg}", file=self.stream)
            return
        print(self.status(symbol, msg, "0;36"), file=self.stream)

    def json(
        self,
        data: Any,
        status: str | None = None,
        indent: int = 2,
        exit_code: int | None = None,
    ) -> None:
        """Standardized JSON emitter for Iceberg CLI tools and automation pipelines."""
        payload: Any
        if isinstance(data, dict):
            payload = dict(data)
            if status is not None and "status" not in payload:
                payload = {"status": status, **payload}
        elif isinstance(data, list):
            if status is not None:
                payload = {"status": status, "items": data}
            else:
                payload = data
        else:
            payload = {"status": status or "ok", "value": data} if status is not None else data

        print(json.dumps(payload, indent=indent, default=str), file=self.stream)
        if exit_code is not None:
            sys.exit(exit_code)

    def version(self, version_str: str, app_name: str | None = None) -> None:
        """Outputs standardized version string matching agent, JSON, and human expectations."""
        name = app_name or self.app_name
        clean_ver = version_str.lstrip("v")
        if self._json_mode:
            self.json({"status": "ok", "app": name, "version": clean_ver})
            return
        if self._agent_mode:
            print(f"{name} {clean_ver}", file=self.stream)
            return
        print(f"{self.badge()} {name} {clean_ver} (v{clean_ver})", file=self.stream)

    def header(self, title: str, width: int = 76) -> None:
        if self._agent_mode:
            clean_title = strip_emojis(strip_ansi(title)).strip()
            print(f"\n=== {clean_title} ===", file=self.stream)
            return
        border = self.blue("=" * width)
        print(f"\n{border}\n {self.bold(title)}\n{border}", file=self.stream)

    def subheader(self, title: str, width: int = 76) -> None:
        if self._agent_mode:
            clean_title = strip_emojis(strip_ansi(title)).strip()
            print(f"\n--- {clean_title} ---", file=self.stream)
            return
        rule_part = self.dim("-" * max(0, width - len(title) - 5))
        print(f"\n{self.cyan(f'--- {title}')} {rule_part}", file=self.stream)
