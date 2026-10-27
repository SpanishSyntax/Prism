"""Low-level POSIX terminal raw I/O, ANSI stripping, and keypress decoder."""

from __future__ import annotations

import os
import re
import select
import shutil
import sys
import termios
import tty
from contextlib import contextmanager
from typing import Iterator, TextIO

ANSI_REGEX = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def strip_ansi(text: str) -> str:
    """Strips ANSI escape sequences to compute visual character length."""
    return ANSI_REGEX.sub("", text)


def visual_len(text: str) -> int:
    """Calculates visible character width on terminal (excluding ANSI codes)."""
    return len(strip_ansi(text))


def get_terminal_columns(fallback: int = 80) -> int:
    """Returns the current terminal width in columns."""
    return shutil.get_terminal_size(fallback=(fallback, 24)).columns


def get_terminal_size(fallback: tuple[int, int] = (80, 24)) -> tuple[int, int]:
    """Returns the current terminal width and height in (columns, lines)."""
    size = shutil.get_terminal_size(fallback=fallback)
    return size.columns, size.lines


@contextmanager
def raw_mode(stream: TextIO | None = None) -> Iterator[int]:
    """Context manager setting standard input into raw mode."""
    target = stream or sys.stdin
    try:
        fd = target.fileno()
    except (io_error(), AttributeError, ValueError):
        yield -1
        return

    if not hasattr(target, "isatty") or not target.isatty():
        yield fd
        return

    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield fd
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def io_error() -> type[Exception]:
    return (io.UnsupportedOperation, OSError) if "io" in globals() else OSError


def read_key(
    stream: TextIO | None = None,
    timeout: float = 0.025,
    raw_text_mode: bool = False,
) -> str:
    """
    Reads a single raw keypress or ANSI escape sequence directly from stdin.
    Uses os.read() without TextIOWrapper buffering to ensure escape sequences
    arrive atomically and reliably in modern terminal emulators.
    """
    target = stream or sys.stdin
    try:
        fd = target.fileno()
    except (OSError, AttributeError, ValueError):
        line = target.readline() if hasattr(target, "readline") else ""
        return line.strip() if line else "enter"

    if not hasattr(target, "isatty") or not target.isatty():
        line = target.readline() if hasattr(target, "readline") else ""
        return line.strip() if line else "enter"

    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        raw = os.read(fd, 32)
        if not raw:
            return "ctrl_d"

        # Check if escape sequence prefix
        if raw == b"\x1b":
            r, _, _ = select.select([fd], [], [], timeout)
            if r:
                raw += os.read(fd, 32)
            else:
                return "esc"

        # Arrow keys & cursor navigation (handles \x1b[A, \x1bOA, \x1b[1;2A, \x1b[[A, etc.)
        if raw.startswith(b"\x1b") and raw.endswith(b"A"):
            return "up"
        if raw.startswith(b"\x1b") and raw.endswith(b"B"):
            return "down"
        if raw.startswith(b"\x1b") and raw.endswith(b"C"):
            return "right"
        if raw.startswith(b"\x1b") and raw.endswith(b"D"):
            return "left"

        # Common functional sequences
        if b"[5~" in raw:
            return "page_up"
        if b"[6~" in raw:
            return "page_down"
        if b"[3~" in raw:
            return "delete"
        if b"[H" in raw or b"OH" in raw:
            return "home"
        if b"[F" in raw or b"OF" in raw:
            return "end"

        # Enter, space, vim navigation, controls
        if raw in (b"\r", b"\n"):
            return "enter"
        if raw == b" ":
            return "space"
        if raw in (b"\x7f", b"\x08"):
            return "backspace"
        if raw == b"\t":
            return "tab"
        if raw == b"\x03":
            return "ctrl_c"
        if raw == b"\x04":
            return "ctrl_d"
        if raw == b"/":
            return "/"

        if not raw_text_mode:
            if raw in (b"k", b"K"):
                return "up"
            if raw in (b"j", b"J"):
                return "down"
            if raw in (b"a", b"A"):
                return "a"
            if raw in (b"q", b"Q"):
                return "q"

        return raw.decode("utf-8", errors="ignore")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# Raw mode and cbreak mode aliases
cbreak_mode = raw_mode
get_key = read_key


