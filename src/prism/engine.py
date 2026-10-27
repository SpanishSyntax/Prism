"""High-level unified UI engine and facade for CLI applications."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Sequence, TextIO

from prism.inputs import confirm_input, prompt_input
from prism.menus import multiselect_menu, select_menu
from prism.panels import render_error_panel, render_panel
from prism.spinner import Spinner
from prism.styling import Styler
from prism.terminal import get_terminal_columns, strip_ansi, visual_len


class UI:
    """
    Unified terminal interface facade for icebergs.
    Provides styling, badges, box panels, braille spinners, prompts, and menus.
    """

    def __init__(
        self,
        app_name: str = "prism",
        icon: str = "🌈",
        badge_color: str = "1;36",
        stream: TextIO | None = None,
        color_mode: str = "auto",
    ) -> None:
        self.styler = Styler(
            app_name=app_name,
            icon=icon,
            badge_color=badge_color,
            color_mode=color_mode,
            stream=stream,
        )

    # Stream & Color Configuration
    def set_stream(self, stream: TextIO) -> None:
        self.styler.set_stream(stream)

    def set_color_mode(self, mode: str) -> None:
        self.styler.set_color_mode(mode)

    @property
    def use_color(self) -> bool:
        return self.styler.use_color

    @property
    def stream(self) -> TextIO:
        return self.styler.stream

    # Color & Text Formatting
    def style(self, text: str, code: str) -> str:
        return self.styler.style(text, code)

    def bold(self, text: str) -> str:
        return self.styler.bold(text)

    def dim(self, text: str) -> str:
        return self.styler.dim(text)

    def italic(self, text: str) -> str:
        return self.styler.italic(text)

    def underline(self, text: str) -> str:
        return self.styler.underline(text)

    def blue(self, text: str) -> str:
        return self.styler.blue(text)

    def cyan(self, text: str) -> str:
        return self.styler.cyan(text)

    def bold_cyan(self, text: str) -> str:
        return self.styler.bold_cyan(text)

    def green(self, text: str) -> str:
        return self.styler.green(text)

    def bold_green(self, text: str) -> str:
        return self.styler.bold_green(text)

    def yellow(self, text: str) -> str:
        return self.styler.yellow(text)

    def red(self, text: str) -> str:
        return self.styler.red(text)

    def magenta(self, text: str) -> str:
        return self.styler.magenta(text)

    # Badges & Status Logs
    def badge(self) -> str:
        return self.styler.badge()

    def status(self, symbol: str, message: str, code: str = "1") -> str:
        return self.styler.status(symbol, message, code)

    def success(self, msg: str) -> None:
        self.styler.success(msg)

    def info(self, msg: str, symbol: str = "ℹ️") -> None:
        self.styler.info(msg, symbol=symbol)

    def warn(self, msg: str) -> None:
        self.styler.warn(msg)

    def error(self, msg: str) -> None:
        self.styler.error(msg)

    def action(self, msg: str, symbol: str = "⚡") -> None:
        self.styler.action(msg, symbol=symbol)

    def header(self, title: str, width: int = 76) -> None:
        self.styler.header(title, width=width)

    def subheader(self, title: str, width: int = 76) -> None:
        self.styler.subheader(title, width=width)

    # Panels & Bounding Boxes
    def panel(
        self,
        title: str,
        lines: Sequence[str] | str,
        border_color: str = "0;36",
        width: int = 76,
        stream: TextIO | None = None,
    ) -> None:
        render_panel(
            title=title,
            lines=lines,
            border_color=border_color,
            width=width,
            styler=self.styler,
            stream=stream or self.stream,
        )

    def error_panel(self, title: str, lines: Sequence[str] | str) -> None:
        render_error_panel(
            title=title,
            lines=lines,
            styler=self.styler,
        )

    # Spinners
    @contextmanager
    def spinner(self, message: str) -> Iterator[Spinner]:
        sp = Spinner(message, styler=self.styler, stream=self.stream)
        sp.start()
        try:
            yield sp
        except Exception:
            sp.stop(ok=False)
            raise
        else:
            sp.stop(ok=True)

    # Prompts & Inputs
    def prompt(self, message: str, default: str = "") -> str:
        return prompt_input(
            message=message,
            default=default,
            styler=self.styler,
            stream=self.stream,
        )

    def confirm(self, message: str, default: bool = False) -> bool:
        return confirm_input(
            message=message,
            default=default,
            styler=self.styler,
            stream=self.stream,
        )

    # Interactive Menus
    def select(
        self,
        title: str,
        options: Sequence[Any],
        default_index: int = 0,
    ) -> str:
        return select_menu(
            title=title,
            options=options,
            default_index=default_index,
            styler=self.styler,
            stream=self.stream,
        )

    def multiselect(
        self,
        title: str,
        options: Sequence[Any],
        preselected: Sequence[str] | set[str] | None = None,
        searchable: bool = True,
    ) -> list[str]:
        return multiselect_menu(
            title=title,
            options=options,
            preselected=preselected,
            styler=self.styler,
            stream=self.stream,
            searchable=searchable,
        )

    # Helpers
    @staticmethod
    def strip_ansi(text: str) -> str:
        return strip_ansi(text)

    @staticmethod
    def visual_len(text: str) -> int:
        return visual_len(text)

    @staticmethod
    def get_terminal_columns(fallback: int = 80) -> int:
        return get_terminal_columns(fallback=fallback)


# Default global instance
ui = UI()
