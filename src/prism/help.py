"""Declarative CLI help and manual generator for human and agent environments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from prism.styling import Styler


class HelpBuilder:
    """Declarative CLI Help and manual builder.

    Produces rich ANSI-highlighted documentation in interactive terminal mode,
    and clean, unescaped, concise reference text in agent automation mode.
    """

    def __init__(
        self,
        app_name: str,
        tagline: str,
        version: str | None = None,
        styler: Styler | None = None,
    ) -> None:
        self.app_name = app_name
        self.tagline = tagline
        self.version = version
        self.styler = styler
        self._usage: list[str] = []
        self._commands: list[tuple[str, str]] = []
        self._options: list[tuple[str, str]] = []
        self._sections: list[tuple[str, list[tuple[str, str]] | str]] = []
        self._examples: list[tuple[str, str]] = []

    def set_usage(self, usage: Sequence[str] | str) -> HelpBuilder:
        if isinstance(usage, str):
            self._usage = [usage]
        else:
            self._usage = list(usage)
        return self

    def add_command(self, name: str, description: str) -> HelpBuilder:
        self._commands.append((name, description))
        return self

    def add_commands(
        self, commands: Sequence[tuple[str, str]] | dict[str, str]
    ) -> HelpBuilder:
        items = commands.items() if isinstance(commands, dict) else commands
        for name, desc in items:
            self._commands.append((name, desc))
        return self

    def add_option(self, flags: str, description: str) -> HelpBuilder:
        self._options.append((flags, description))
        return self

    def add_options(
        self, options: Sequence[tuple[str, str]] | dict[str, str]
    ) -> HelpBuilder:
        items = options.items() if isinstance(options, dict) else options
        for flags, desc in items:
            self._options.append((flags, desc))
        return self

    def add_section(
        self, title: str, content: Sequence[tuple[str, str]] | str
    ) -> HelpBuilder:
        if isinstance(content, str):
            self._sections.append((title, content))
        else:
            self._sections.append((title, list(content)))
        return self

    def add_example(self, command: str, comment: str = "") -> HelpBuilder:
        self._examples.append((command, comment))
        return self

    def add_examples(
        self, examples: Sequence[tuple[str, str]] | Sequence[str]
    ) -> HelpBuilder:
        for ex in examples:
            if isinstance(ex, tuple):
                self._examples.append(ex)
            else:
                self._examples.append((ex, ""))
        return self

    def render(self, is_agent: bool | None = None) -> str:
        from prism.engine import ui as default_ui

        st = self.styler or default_ui.styler
        agent = st.is_agent if is_agent is None else is_agent

        lines: list[str] = []

        # 1. Header
        clean_tagline = self.tagline.strip()
        if agent:
            v_part = f" v{self.version.lstrip('v')}" if self.version else ""
            lines.append(f"{self.app_name}{v_part} - {clean_tagline}")
        else:
            v_part = f" v{self.version.lstrip('v')}" if self.version else ""
            lines.append(f"{st.badge()} {st.bold(f'{clean_tagline}{v_part}')}")

        # 2. Usage
        if self._usage:
            lines.append("")
            if agent:
                if len(self._usage) == 1:
                    lines.append(f"Usage: {self._usage[0]}")
                else:
                    lines.append(f"Usage: {self._usage[0]}")
                    for u in self._usage[1:]:
                        lines.append(f"       {u}")
            else:
                lines.append(st.blue("Usage:"))
                for u in self._usage:
                    lines.append(f"  {u}")

        # Helper for key-value table formatting
        def format_kv(
            items: list[tuple[str, str]], indent: int = 2, col_width: int = 24
        ) -> list[str]:
            res: list[str] = []
            pad = " " * indent
            # Find max key length, capped at col_width
            actual_col_w = max([len(k) for k, _ in items] + [col_width])
            for k, v in items:
                v_lines = v.split("\n")
                first = f"{pad}{k:<{actual_col_w}} {v_lines[0]}".rstrip()
                res.append(first)
                cont_pad = " " * (indent + actual_col_w + 1)
                for cont in v_lines[1:]:
                    res.append(f"{cont_pad}{cont}")
            return res

        # 3. Commands
        if self._commands:
            lines.append("")
            lines.append("Commands:" if agent else st.blue("Commands:"))
            lines.extend(format_kv(self._commands))

        # 4. Custom Sections before Options (if any)
        for title, content in self._sections:
            lines.append("")
            title_header = f"{title}:" if not title.endswith(":") else title
            lines.append(title_header if agent else st.blue(title_header))
            if isinstance(content, str):
                lines.extend(
                    f"  {line}" if not line.startswith("  ") else line
                    for line in content.split("\n")
                )
            else:
                lines.extend(format_kv(content))

        # 5. Options
        if self._options:
            lines.append("")
            lines.append("Options:" if agent else st.blue("Options:"))
            lines.extend(format_kv(self._options))

        # 6. Examples
        if self._examples:
            lines.append("")
            lines.append("Examples:" if agent else st.blue("Examples:"))
            pad = "  "
            max_cmd_len = max((len(c) for c, _ in self._examples), default=20)
            col_w = max(24, max_cmd_len + 2)
            for cmd, comment in self._examples:
                if comment:
                    if agent:
                        lines.append(f"{pad}{cmd:<{col_w}} # {comment}")
                    else:
                        lines.append(f"{pad}{cmd:<{col_w}} {st.dim(f'# {comment}')}")
                else:
                    lines.append(f"{pad}{cmd}")

        return "\n".join(lines) + "\n"

    def __str__(self) -> str:
        return self.render()


def render_help(
    app_name: str,
    tagline: str,
    usage: Sequence[str] | str,
    commands: Sequence[tuple[str, str]] | dict[str, str] | None = None,
    options: Sequence[tuple[str, str]] | dict[str, str] | None = None,
    sections: Sequence[tuple[str, Sequence[tuple[str, str]] | str]] | None = None,
    examples: Sequence[tuple[str, str]] | Sequence[str] | None = None,
    version: str | None = None,
    styler: Styler | None = None,
    is_agent: bool | None = None,
) -> str:
    """Helper function to declaratively render styled help documentation."""
    hb = HelpBuilder(
        app_name=app_name, tagline=tagline, version=version, styler=styler
    )
    hb.set_usage(usage)
    if commands:
        hb.add_commands(commands)
    if sections:
        for t, c in sections:
            hb.add_section(t, c)
    if options:
        hb.add_options(options)
    if examples:
        hb.add_examples(examples)
    return hb.render(is_agent=is_agent)
