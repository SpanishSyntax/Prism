"""Multi-threaded zero-dependency braille spinner for background operations."""

from __future__ import annotations

import sys
import threading
from contextlib import contextmanager
from typing import Iterator, TextIO

from prism.styling import Styler


class Spinner:
    """Zero-dependency braille terminal spinner for long-running CLI tasks."""

    FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    def __init__(
        self,
        message: str,
        styler: Styler | None = None,
        stream: TextIO | None = None,
    ) -> None:
        self.message = message
        self.styler = styler or Styler()
        self.stream = stream or self.styler.stream
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._is_tty = hasattr(self.stream, "isatty") and self.stream.isatty()

    def update(self, message: str) -> None:
        """Updates the active spinner status text dynamically."""
        self.message = message

    def _spin(self) -> None:
        idx = 0
        while not self._stop_event.is_set():
            frame = self.styler.bold_cyan(self.FRAMES[idx % len(self.FRAMES)])
            line = f"\r\033[2K{self.styler.badge()} {frame} {self.message}"
            self.stream.write(line)
            self.stream.flush()
            idx += 1
            self._stop_event.wait(0.08)

    def start(self) -> None:
        """Starts the spinner thread."""
        if self.styler.is_agent:
            return
        if not self._is_tty:
            self.styler.action(self.message, symbol="⏳")
            return
        self.stream.write("\033[?25l")
        self.stream.flush()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, final_message: str | None = None, ok: bool = True) -> None:
        """Stops the spinner and restores cursor."""
        if self.styler.is_agent:
            if final_message:
                if ok:
                    self.styler.success(final_message)
                else:
                    self.styler.error(final_message)
            return
        if not self._is_tty:
            if final_message:
                if ok:
                    self.styler.success(final_message)
                else:
                    self.styler.error(final_message)
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self.stream.write("\r\033[2K\033[?25h")
        self.stream.flush()
        if final_message:
            if ok:
                self.styler.success(final_message)
            else:
                self.styler.error(final_message)


@contextmanager
def spinner_context(
    message: str,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> Iterator[Spinner]:
    """Context manager for spinner execution."""
    sp = Spinner(message, styler=styler, stream=stream)
    sp.start()
    try:
        yield sp
    except Exception:
        sp.stop(ok=False)
        raise
    else:
        sp.stop(ok=True)
