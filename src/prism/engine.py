"""High-level unified UI engine and facade for CLI applications."""

from __future__ import annotations

from contextlib import contextmanager
import weakref
from typing import Any, Iterator, Sequence, TextIO

from prism.inputs import confirm_input, prompt_input
from prism.menus import multiselect_menu, select_menu
from prism.panels import render_error_panel, render_panel
from prism.spinner import Spinner
from prism.styling import Styler
from prism.terminal import get_terminal_columns, strip_ansi, visual_len


_registered_instances: list[weakref.ref[UI]] = []


def get_all_ui_instances() -> list[UI]:
    """Returns all currently live UI instances."""
    live = []
    for ref in list(_registered_instances):
        inst = ref()
        if inst is not None:
            live.append(inst)
        else:
            _registered_instances.remove(ref)
    return live


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
        agent_mode: bool | None = None,
    ) -> None:
        self.styler = Styler(
            app_name=app_name,
            icon=icon,
            badge_color=badge_color,
            color_mode=color_mode,
            stream=stream,
            agent_mode=agent_mode,
        )
        _registered_instances.append(weakref.ref(self))

    # Stream & Color Configuration
    def set_stream(self, stream: TextIO) -> None:
        self.styler.set_stream(stream)

    def set_color_mode(self, mode: str) -> None:
        self.styler.set_color_mode(mode)

    def set_agent_mode(self, agent: bool = True, json_output: bool = False) -> None:
        self.styler.set_agent_mode(agent=agent, json_output=json_output)

    @property
    def is_agent(self) -> bool:
        return self.styler.is_agent

    @property
    def is_json(self) -> bool:
        return self.styler.is_json

    @property
    def is_interactive(self) -> bool:
        return self.styler.is_interactive

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

    def json(
        self,
        data: Any,
        status: str | None = None,
        indent: int = 2,
        exit_code: int | None = None,
    ) -> None:
        self.styler.json(data=data, status=status, indent=indent, exit_code=exit_code)

    def version(self, version_str: str, app_name: str | None = None) -> None:
        self.styler.version(version_str=version_str, app_name=app_name)

    def handle_version_arg(
        self,
        raw_args: Sequence[str],
        version_str: str,
        app_name: str | None = None,
    ) -> bool:
        from prism.color import handle_version_arg

        return handle_version_arg(
            raw_args=raw_args,
            version_str=version_str,
            app_name=app_name,
            ui=self,
        )

    def render_help(
        self,
        tagline: str,
        usage: Sequence[str] | str,
        commands: Sequence[tuple[str, str]] | dict[str, str] | None = None,
        options: Sequence[tuple[str, str]] | dict[str, str] | None = None,
        sections: Sequence[tuple[str, Sequence[tuple[str, str]] | str]] | None = None,
        examples: Sequence[tuple[str, str]] | Sequence[str] | None = None,
        version: str | None = None,
        app_name: str | None = None,
        is_agent: bool | None = None,
    ) -> str:
        from prism.help import render_help

        return render_help(
            app_name=app_name or self.styler.app_name,
            tagline=tagline,
            usage=usage,
            commands=commands,
            options=options,
            sections=sections,
            examples=examples,
            version=version,
            styler=self.styler,
            is_agent=is_agent,
        )

    def print_help(
        self,
        tagline: str,
        usage: Sequence[str] | str,
        commands: Sequence[tuple[str, str]] | dict[str, str] | None = None,
        options: Sequence[tuple[str, str]] | dict[str, str] | None = None,
        sections: Sequence[tuple[str, Sequence[tuple[str, str]] | str]] | None = None,
        examples: Sequence[tuple[str, str]] | Sequence[str] | None = None,
        version: str | None = None,
        app_name: str | None = None,
        is_agent: bool | None = None,
    ) -> None:
        doc = self.render_help(
            tagline=tagline,
            usage=usage,
            commands=commands,
            options=options,
            sections=sections,
            examples=examples,
            version=version,
            app_name=app_name,
            is_agent=is_agent,
        )
        print(doc, end="", file=self.stream)

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
