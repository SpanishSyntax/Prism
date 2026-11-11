"""Standardized status card and runtime dashboard widgets for human and agent environments."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TextIO

from prism.panels import render_panel

if TYPE_CHECKING:
    from prism.styling import Styler


def render_status_card(
    title: str,
    target: str | None = None,
    url: str | None = None,
    details: Sequence[tuple[str, str]] | dict[str, str] | None = None,
    controls: Sequence[tuple[str, str]] | None = None,
    warning: str | None = None,
    tip: str | None = None,
    border_color: str = "1;36",
    width: int = 76,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> None:
    """Renders a standardized status card for live services, daemons, watchers, and tasks.

    In interactive human terminal mode:
      Emits a styled rounded card with title, target/URL endpoint, property details,
      ephemeral warning notices, and hotkey controls.

    In AI / Agent mode:
      Emits a token-efficient single-line status declaration without box borders,
      ANSI escape sequences, or decorative formatting.
    """
    from prism.engine import ui as default_ui

    st = styler or default_ui.styler
    out = stream or st.stream

    from prism.terminal import strip_ansi, strip_emojis

    # Structured JSON Mode
    if st.is_json:
        import json

        payload: dict[str, Any] = {
            "status": "active",
            "title": strip_emojis(strip_ansi(title)),
        }
        if url:
            payload["url"] = url
        if target:
            payload["target"] = target
        if details:
            items = details.items() if isinstance(details, dict) else details
            for k, v in items:
                payload[k.lower().replace(" ", "_")] = v
        out.write(json.dumps(payload, indent=2) + "\n")
        return

    # Structured TOON Mode
    if st.is_toon:
        from prism.toon import encode_toon

        payload = {
            "status": "active",
            "title": strip_emojis(strip_ansi(title)),
        }
        if url:
            payload["url"] = url
        if target:
            payload["target"] = target
        if details:
            items = details.items() if isinstance(details, dict) else details
            for k, v in items:
                payload[k.lower().replace(" ", "_")] = v
        out.write(encode_toon(payload) + "\n")
        return

    # AI / Agent Mode: Token-efficient, single-line machine output
    if st.is_agent:
        clean_title = strip_emojis(strip_ansi(title))
        parts = [f'STATUS_ACTIVE: title="{clean_title}"']
        if url:
            parts.append(f'url="{url}"')
        if target:
            parts.append(f'target="{target}"')
        if details:
            items = details.items() if isinstance(details, dict) else details
            for k, v in items:
                parts.append(f'{k.lower().replace(" ", "_")}="{v}"')
        out.write(" ".join(parts) + "\n")
        return

    # Interactive Human Terminal Mode
    lines: list[str] = []
    if url:
        lines.append(f"Endpoint:     {st.bold_cyan(url)}")
    if target:
        lines.append(f"Target:       {st.bold(target)}")

    if details:
        items = details.items() if isinstance(details, dict) else details
        for k, v in items:
            key_col = f"{k + ':':<14}"
            lines.append(f"{key_col}{v}")

    if warning:
        if lines:
            lines.append("")
        lines.append(st.yellow(f"⚠️  {warning}"))

    if tip:
        if not warning and lines:
            lines.append("")
        lines.append(st.dim(f"   {tip}"))

    if controls:
        if lines:
            lines.append("")
        ctrl_strs = [f"{st.bold(key)} {label}" for key, label in controls]
        lines.append(f"Controls:     {'  |  '.join(ctrl_strs)}")

    render_panel(
        title=title,
        lines=lines,
        border_color=border_color,
        width=width,
        styler=st,
        stream=out,
    )
