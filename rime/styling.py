"""ANSI color formatting, styling primitives, and status badge generator."""

from __future__ import annotations

import os
import sys
from typing import TextIO


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
        app_name: str = "rime",
        icon: str = "🧊",
        badge_color: str = "1;36",
        color_mode: str = "auto",
        stream: TextIO | None = None,
    ) -> None:
        self.app_name = app_name
        self.icon = icon
        self.badge_color = badge_color
        self._color_mode = color_mode
        self._stream = stream

    @property
    def stream(self) -> TextIO:
        return self._stream if self._stream is not None else sys.stdout

    def set_stream(self, stream: TextIO) -> None:
        self._stream = stream

    def set_color_mode(self, mode: str) -> None:
        self._color_mode = mode.lower()

    @property
    def use_color(self) -> bool:
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
        return self.style(f"{self.icon} [{self.app_name}]", self.badge_color)

    def status(self, symbol: str, message: str, code: str = "1") -> str:
        return f"{self.badge()} {self.style(f'{symbol} {message}', code)}"

    def success(self, msg: str) -> None:
        print(self.status("✔", msg, "1;32"), file=self.stream)

    def info(self, msg: str, symbol: str = "ℹ️") -> None:
        print(self.status(symbol, msg, "1;34"), file=self.stream)

    def warn(self, msg: str) -> None:
        print(self.status("⚠️", msg, "1;33"), file=self.stream)

    def error(self, msg: str) -> None:
        print(self.status("✘", msg, "1;31"), file=sys.stderr)

    def action(self, msg: str, symbol: str = "⚡") -> None:
        print(self.status(symbol, msg, "0;36"), file=self.stream)

    def header(self, title: str, width: int = 76) -> None:
        border = self.blue("=" * width)
        print(f"\n{border}\n {self.bold(title)}\n{border}", file=self.stream)

    def subheader(self, title: str, width: int = 76) -> None:
        rule_part = self.dim("-" * max(0, width - len(title) - 5))
        print(f"\n{self.cyan(f'--- {title}')} {rule_part}", file=self.stream)
