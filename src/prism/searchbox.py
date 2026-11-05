"""Zero-dependency interactive searchbox and real-time fuzzy selector widget."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TextIO

from prism.menus import normalize_options
from prism.terminal import (
    get_terminal_columns,
    get_terminal_size,
    read_key,
    strip_ansi,
    visual_len,
)

if TYPE_CHECKING:
    from prism.styling import Styler


def searchbox(
    title: str = "Search",
    options: Sequence[Any] = (),
    prompt: str = "❯ ",
    placeholder: str = "Type to search...",
    limit: int = 10,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> str | None:
    """Interactive real-time searchbox with instant keystroke filtering.

    Allows immediate text entry to filter options dynamically. Arrow keys (or Tab)
    navigate between filtered matches, ENTER selects, and ESC/Ctrl+C cancels.

    In AI / Agent mode or non-interactive environments:
      Returns the first available option key without hanging or consuming extra tokens.
    """
    from prism.engine import ui as default_ui

    st = styler or default_ui.styler
    out = stream or st.stream
    all_items = normalize_options(options)

    if not all_items:
        return None

    # Agent Mode / Non-TTY fallback
    if st.is_agent or not sys.stdin.isatty():
        return all_items[0][0]

    query = ""
    selected_idx = 0

    def _filter_items(q: str) -> list[tuple[str, str, str]]:
        if not q.strip():
            return all_items
        tokens = q.lower().split()
        return [
            item
            for item in all_items
            if all(
                tok in f"{item[0]} {strip_ansi(item[1])} {strip_ansi(item[2])}".lower()
                for tok in tokens
            )
        ]

    # Hide cursor
    out.write("\033[?25l")
    out.flush()

    rendered_line_count = 0

    try:
        while True:
            # Clear previous render
            if rendered_line_count > 0:
                out.write(f"\033[{rendered_line_count}F")
                for _ in range(rendered_line_count):
                    out.write("\033[2K\n")
                out.write(f"\033[{rendered_line_count}F")
                out.flush()

            matches = _filter_items(query)
            if selected_idx >= len(matches):
                selected_idx = max(0, len(matches) - 1)

            term_cols = get_terminal_columns(fallback=80)
            max_w = max(36, term_cols - 2)

            lines: list[str] = []

            # 1. Header with live match count
            count_badge = st.dim(f"[{len(matches)}/{len(all_items)} matches]")
            lines.append(f"{st.badge()} {st.bold(title)}  {count_badge}")

            # 2. Search prompt and active query
            disp_query = query if query else st.dim(placeholder)
            cursor = st.bold_cyan("█")
            lines.append(f"  {st.bold_cyan(prompt)}{disp_query}{cursor}")
            lines.append(f"  {st.dim('─' * min(max_w, 60))}")

            # 3. Visible list of matching items
            window_size = min(limit, 15)
            start_idx = 0
            if selected_idx >= window_size:
                start_idx = selected_idx - window_size + 1
            visible_matches = matches[start_idx : start_idx + window_size]

            if not matches:
                lines.append(f"  {st.dim('No matches found for \"')}{st.yellow(query)}{st.dim('\"')}")
            else:
                for idx_offset, (k, lbl, desc) in enumerate(visible_matches):
                    actual_idx = start_idx + idx_offset
                    is_active = actual_idx == selected_idx

                    pointer = st.bold_cyan("❯ ") if is_active else "  "
                    label_str = st.bold(lbl) if is_active else lbl
                    desc_str = f"  {st.dim(desc)}" if desc else ""

                    full_item = f"{pointer}{label_str}{desc_str}"
                    # Truncate to terminal width
                    if visual_len(full_item) > max_w:
                        plain = strip_ansi(full_item)
                        full_item = plain[: max_w - 3] + "..."

                    lines.append(f"  {full_item}")

            # 4. Helper footer
            lines.append(f"  {st.dim('Type to filter | ↑↓ to navigate | Enter to select | Esc to cancel')}")

            # Write all lines atomically
            output_text = "\n".join(lines) + "\n"
            out.write(output_text)
            out.flush()
            rendered_line_count = len(lines)

            # Read keystroke
            key = read_key(raw_text_mode=True)

            if key in ("enter", "\r", "\n"):
                if matches and 0 <= selected_idx < len(matches):
                    return matches[selected_idx][0]
                return None
            elif key in ("esc", "ctrl_c", "ctrl_d"):
                return None
            elif key in ("up", "\x1b[A", "page_up"):
                if selected_idx > 0:
                    selected_idx -= 1
                elif matches:
                    selected_idx = len(matches) - 1
            elif key in ("down", "\x1b[B", "tab", "page_down"):
                if selected_idx < len(matches) - 1:
                    selected_idx += 1
                else:
                    selected_idx = 0
            elif key in ("backspace", "\x7f", "\x08"):
                if query:
                    query = query[:-1]
                    selected_idx = 0
            elif len(key) == 1 and key.isprintable():
                query += key
                selected_idx = 0

    finally:
        # Restore cursor
        out.write("\033[?25h")
        out.flush()
