"""Rounded box panel rendering, width-aware layout, and diagnostic boxes."""

from __future__ import annotations

import sys
from typing import Sequence, TextIO

from prism.styling import Styler
from prism.terminal import get_terminal_columns, strip_ansi, strip_emojis, visual_len


def render_panel(
    title: str,
    lines: Sequence[str] | str,
    border_color: str = "0;36",
    width: int = 76,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> None:
    """Renders a width-aware rounded box panel (╭─╮│╰─╯) to stream."""
    st = styler or Styler()
    out = stream or st.stream
    body_lines = lines.splitlines() if isinstance(lines, str) else list(lines)

    if st.is_agent:
        title_clean = strip_emojis(strip_ansi(title)).strip()
        if title_clean:
            print(f"=== {title_clean} ===", file=out)
        for line in body_lines:
            print(strip_ansi(line), file=out)
        print(file=out)
        return

    term_cols = get_terminal_columns(fallback=80)
    box_w = min(width, max(36, term_cols - 2))
    inner_w = box_w - 4

    title_clean = strip_ansi(title)
    title_segment = f" {title} " if title else ""
    top_fill = max(1, box_w - 3 - len(title_clean) - (2 if title else 0))
    top_border = (
        st.style("╭─", border_color)
        + (st.bold(title_segment) if title else "")
        + st.style("─" * top_fill + "╮", border_color)
    )
    bottom_border = st.style("╰" + "─" * (box_w - 2) + "╯", border_color)
    side = st.style("│", border_color)

    print(top_border, file=out)
    for raw_line in body_lines:
        vis_len = visual_len(raw_line)
        if vis_len <= inner_w:
            pad = " " * (inner_w - vis_len)
            print(f"{side} {raw_line}{pad} {side}", file=out)
        else:
            plain = strip_ansi(raw_line)
            clipped = plain[: max(0, inner_w - 3)] + "..."
            pad = " " * max(0, inner_w - len(clipped))
            print(f"{side} {clipped}{pad} {side}", file=out)
    print(bottom_border, file=out)


def render_error_panel(
    title: str,
    lines: Sequence[str] | str,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> None:
    """Renders an error diagnostic panel with red border to stderr."""
    st = styler or Styler()
    out = stream or sys.stderr

    if st.is_agent:
        title_clean = strip_emojis(strip_ansi(title)).strip()
        print(f"ERROR: {title_clean}", file=out)
        body_lines = lines.splitlines() if isinstance(lines, str) else list(lines)
        for line in body_lines:
            print(strip_ansi(line), file=out)
        return

    styled_title = st.red(f"✘ {title}")
    render_panel(
        title=styled_title,
        lines=lines,
        border_color="1;31",
        styler=st,
        stream=out,
    )
