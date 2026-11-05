"""Dev server and live service status banner widgets for human and agent environments."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TextIO

from prism.panels import render_panel
from prism.terminal import visual_len

if TYPE_CHECKING:
    from prism.styling import Styler


def render_serve_banner(
    title: str,
    url: str,
    target: str | None = None,
    details: Sequence[tuple[str, str]] | dict[str, str] | None = None,
    controls: Sequence[tuple[str, str]] | None = None,
    warning: str | None = None,
    tip: str | None = None,
    border_color: str = "1;36",
    width: int = 76,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> None:
    """Renders a standardized dev-server or service status banner.

    In interactive human terminal mode:
      Emits a Prism-styled box panel with URL, Target, runtime details,
      ephemeral warnings, and interactive hotkey controls.

    In AI / Agent mode:
      Emits a single-line or compact token-efficient status without box borders,
      ANSI escape sequences, or decorative formatting.
    """
    from prism.engine import ui as default_ui

    st = styler or default_ui.styler
    out = stream or st.stream

    # AI / Agent Mode: Token-efficient, single-line or compact machine output
    if st.is_agent:
        parts = [f"SERVER_ACTIVE: name=\"{title}\"", f"url=\"{url}\""]
        if target:
            parts.append(f"target=\"{target}\"")
        if details:
            items = details.items() if isinstance(details, dict) else details
            for k, v in items:
                parts.append(f"{k.lower().replace(' ', '_')}=\"{v}\"")
        out.write(" ".join(parts) + "\n")
        return

    # Interactive Human Terminal Mode
    lines: list[str] = [
        f"URL:          {st.bold_cyan(url)}",
    ]
    if target:
        lines.append(f"Target:       {st.bold(target)}")

    if details:
        items = details.items() if isinstance(details, dict) else details
        for k, v in items:
            key_col = f"{k + ':':<14}"
            lines.append(f"{key_col}{v}")

    if warning:
        lines.append("")
        lines.append(st.yellow(f"⚠️  {warning}"))

    if tip:
        if not warning:
            lines.append("")
        lines.append(st.dim(f"   {tip}"))

    if controls:
        lines.append("")
        ctrl_strs = [
            f"{st.bold(key)} {label}" for key, label in controls
        ]
        lines.append(f"Controls:     {'  |  '.join(ctrl_strs)}")

    render_panel(
        title=title,
        lines=lines,
        border_color=border_color,
        width=width,
        styler=st,
        stream=out,
    )
