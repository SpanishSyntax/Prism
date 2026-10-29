"""Terminal interactive selection and multi-selection menus with pagination."""

from __future__ import annotations

import sys
from typing import Any, Sequence, TextIO

from prism.styling import Styler
from prism.terminal import (
    get_terminal_size,
    read_key,
    strip_ansi,
    visual_len,
)


def normalize_options(options: Sequence[Any]) -> list[tuple[str, str, str]]:
    """
    Normalizes options into a standard list of (key, label, description).
    Supports:
      - "item" -> (item, item, "")
      - ("key", "label") -> (key, label, "")
      - ("key", "label", "description") -> (key, label, description)
    """
    result = []
    for opt in options:
        if isinstance(opt, (list, tuple)):
            if len(opt) == 1:
                result.append((str(opt[0]), str(opt[0]), ""))
            elif len(opt) == 2:
                result.append((str(opt[0]), str(opt[1]), ""))
            else:
                result.append((str(opt[0]), str(opt[1]), str(opt[2])))
        else:
            result.append((str(opt), str(opt), ""))
    return result


def fit_line(
    prefix: str,
    label_styled: str,
    label_plain: str,
    desc: str,
    max_w: int,
    styler: Styler,
) -> str:
    """
    Ensures a menu item line never exceeds max_w visual columns.
    Prevents terminal wrapping so cursor up/down operations remain 100% in sync.
    """
    prefix_len = visual_len(prefix)
    avail = max_w - prefix_len
    if avail <= 5:
        return prefix + label_plain[: max(0, avail)]

    if not desc:
        if len(label_plain) <= avail:
            return f"{prefix}{label_styled}"
        return f"{prefix}{label_plain[: max(0, avail - 3)]}..."

    # Both label and desc present
    if len(label_plain) + 2 + len(desc) <= avail:
        return f"{prefix}{label_styled} {styler.dim(desc)}"

    # Fit label and truncated description
    if len(label_plain) + 6 <= avail:
        rem = avail - len(label_plain) - 4
        trunc_desc = desc[: max(0, rem)] + "..."
        return f"{prefix}{label_styled} {styler.dim(trunc_desc)}"

    # Narrow terminal: label only
    if len(label_plain) <= avail:
        return f"{prefix}{label_styled}"
    return f"{prefix}{label_plain[: max(0, avail - 3)]}..."


def select_menu(
    title: str,
    options: Sequence[Any],
    default_index: int = 0,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> str:
    """
    Single-select interactive menu with arrow key / j-k navigation.
    Width & height aware: truncates wide lines and paginates lists to fit any terminal size.
    """
    st = styler or Styler()
    if st.is_agent:
        items = normalize_options(options)
        if not items:
            return ""
        idx = max(0, min(default_index, len(items) - 1))
        return items[idx][0]

    out = stream or st.stream
    items = normalize_options(options)
    if not items:
        return ""

    # Fallback for non-interactive / non-TTY
    if not sys.stdin.isatty():
        out.write(f"\n{st.badge()} {st.bold(title)}\n")
        for idx, (_, lbl, desc) in enumerate(items, 1):
            extra = f" - {desc}" if desc else ""
            out.write(f"  [{idx}] {lbl}{extra}\n")
        out.flush()
        try:
            ans = input("Choice [1]: ").strip()
        except (EOFError, OSError):
            ans = ""
        if ans.isdigit() and 1 <= int(ans) <= len(items):
            return items[int(ans) - 1][0]
        return items[0][0]

    current = max(0, min(default_index, len(items) - 1))
    scroll_offset = 0
    rendered_lines = 0

    # Hide cursor
    out.write("\033[?25l")
    out.flush()

    try:
        while True:
            cols, term_rows = get_terminal_size(fallback=(80, 24))
            max_w = max(25, cols - 1)

            # Available vertical rows for items
            max_visible = max(3, min(len(items), term_rows - 5, 10))

            # Keep active item inside scroll window
            if current < scroll_offset:
                scroll_offset = current
            elif current >= scroll_offset + max_visible:
                scroll_offset = current - max_visible + 1
            scroll_offset = max(0, min(scroll_offset, max(0, len(items) - max_visible)))

            lines: list[str] = []
            # Header
            raw_title = f"{st.badge()} {st.bold(title)}"
            lines.append(
                raw_title if visual_len(raw_title) <= max_w else raw_title[:max_w]
            )

            # Subtitle navigation hint
            raw_help = st.dim(
                "  (Use ↑/↓ or j/k to navigate, Enter to select, q/Ctrl+C to cancel)"
            )
            lines.append(
                raw_help
                if visual_len(raw_help) <= max_w
                else st.dim("  (↑/↓: navigate, Enter: select)")
            )
            lines.append("")

            # Up indicator if scrolled
            if scroll_offset > 0:
                lines.append(st.dim(f"  ▲ ({scroll_offset} more above...)"))

            # Visible items
            visible_items = items[scroll_offset : scroll_offset + max_visible]
            for idx_offset, (_, label, desc) in enumerate(visible_items):
                actual_idx = scroll_offset + idx_offset
                if actual_idx == current:
                    pointer = st.bold_cyan("❯")
                    styled_lbl = st.bold_cyan(label)
                else:
                    pointer = " "
                    styled_lbl = label

                prefix = f"  {pointer} "
                lines.append(
                    fit_line(prefix, styled_lbl, label, desc, max_w, styler=st)
                )

            # Down indicator if more below
            if scroll_offset + max_visible < len(items):
                remaining = len(items) - (scroll_offset + max_visible)
                lines.append(st.dim(f"  ▼ ({remaining} more below...)"))

            # Clear previous frame rows and redraw in-place
            if rendered_lines > 0:
                out.write(f"\033[{rendered_lines}A\r")
            for line in lines:
                out.write(f"\033[2K{line}\r\n")
            out.flush()
            rendered_lines = len(lines)

            key = read_key()
            if key in ("up", "k"):
                current = (current - 1) % len(items)
            elif key in ("down", "j"):
                current = (current + 1) % len(items)
            elif key == "enter":
                break
            elif key in ("ctrl_c", "ctrl_d", "q", "esc"):
                if rendered_lines > 0:
                    out.write(f"\033[{rendered_lines}A\r")
                    for _ in range(rendered_lines):
                        out.write("\033[2K\r\n")
                    out.write(f"\033[{rendered_lines}A\r")
                    out.flush()
                out.write("\nAborted.\n")
                out.flush()
                sys.exit(0)

        # Clear interactive frame cleanly and output final choice
        out.write(f"\033[{rendered_lines}A\r")
        for _ in range(rendered_lines):
            out.write("\033[2K\r\n")
        out.write(f"\033[{rendered_lines}A\r")
        out.write(
            f"{st.badge()} {st.dim(title)} {st.bold_green(items[current][1])}\n"
        )
        out.flush()
        return items[current][0]
    finally:
        out.write("\033[?25h")
        out.flush()


def multiselect_menu(
    title: str,
    options: Sequence[Any],
    preselected: Sequence[str] | set[str] | None = None,
    styler: Styler | None = None,
    stream: TextIO | None = None,
    searchable: bool = True,
) -> list[str]:
    """
    Multi-select interactive menu with arrow key navigation, spacebar toggling,
    and optional live `/` search filter.
    Width & height aware: truncates wide lines and paginates lists to fit any terminal size.
    """
    st = styler or Styler()
    if st.is_agent:
        return list(preselected) if preselected else []

    out = stream or st.stream
    all_items = normalize_options(options)
    if not all_items:
        return []

    selected_keys: set[str] = set(preselected) if preselected else set()

    # Fallback for non-interactive / non-TTY
    if not sys.stdin.isatty():
        out.write(f"\n{st.badge()} {st.bold(title)}\n")
        for idx, (k, lbl, desc) in enumerate(all_items, 1):
            mark = "[*]" if k in selected_keys else "[ ]"
            extra = f" - {desc}" if desc else ""
            out.write(f"  {mark} [{idx}] {lbl}{extra}\n")
        out.flush()
        try:
            ans = input("Select numbers (comma/space separated): ").strip()
        except (EOFError, OSError):
            ans = ""
        chosen = []
        for tok in ans.replace(",", " ").split():
            if tok.isdigit() and 1 <= int(tok) <= len(all_items):
                chosen.append(all_items[int(tok) - 1][0])
        return chosen if chosen else [k for k, _, _ in all_items if k in selected_keys]

    current = 0
    scroll_offset = 0
    rendered_lines = 0
    search_query = ""
    searching = False

    def _filter_items() -> list[tuple[str, str, str]]:
        if not search_query.strip():
            return all_items
        tokens = search_query.lower().split()
        return [
            item
            for item in all_items
            if all(tok in f"{item[0]} {item[1]} {item[2]}".lower() for tok in tokens)
        ]

    # Hide cursor
    out.write("\033[?25l")
    out.flush()

    try:
        while True:
            items = _filter_items()
            if items:
                current = max(0, min(current, len(items) - 1))
            else:
                current = 0

            cols, term_rows = get_terminal_size(fallback=(80, 24))
            max_w = max(25, cols - 1)

            # Available vertical rows for items
            max_visible = max(3, min(max(1, len(items)), term_rows - 6, 12))

            # Keep active item inside scroll window
            if current < scroll_offset:
                scroll_offset = current
            elif current >= scroll_offset + max_visible:
                scroll_offset = current - max_visible + 1
            scroll_offset = max(0, min(scroll_offset, max(0, len(items) - max_visible)))

            lines = []
            selected_count = sum(1 for k, _, _ in all_items if k in selected_keys)
            raw_title = f"{st.badge()} {st.bold(title)} {st.dim(f'({selected_count}/{len(all_items)} selected)')}"
            lines.append(
                raw_title if visual_len(raw_title) <= max_w else raw_title[:max_w]
            )

            if searching:
                search_bar = (
                    f"  {st.bold_cyan('🔍 Search:')} {st.bold(search_query)}█ "
                    f"{st.dim('(type to filter, Enter/Esc: done)')}"
                )
                lines.append(
                    search_bar
                    if visual_len(search_bar) <= max_w
                    else f"  {st.bold_cyan('🔍 Search:')} {st.bold(search_query)}█"
                )
            else:
                filter_badge = (
                    f"  {st.yellow(f'Filter: \"{search_query}\"')} {st.dim('(/ to edit, Esc to clear)')} | "
                    if search_query
                    else "  "
                )
                search_hint = "  /: search  " if searchable else "  "
                raw_help = filter_badge + st.dim(
                    f"↑/↓: nav  Space: toggle{search_hint}a: all  Enter: confirm  q: quit"
                )
                lines.append(
                    raw_help
                    if visual_len(raw_help) <= max_w
                    else st.dim("  (↑/↓: nav, Space: toggle, Enter: ok)")
                )
            lines.append("")

            if not items:
                lines.append(
                    st.yellow(
                        f"  No items match '{search_query}'. Press Esc or Backspace to clear filter."
                    )
                )
            else:
                # Up indicator if scrolled
                if scroll_offset > 0:
                    lines.append(st.dim(f"  ▲ ({scroll_offset} more above...)"))

                # Visible items
                visible_items = items[scroll_offset : scroll_offset + max_visible]
                for idx_offset, (key, label, desc) in enumerate(visible_items):
                    actual_idx = scroll_offset + idx_offset
                    is_checked = key in selected_keys
                    check = st.bold_green("[✔]") if is_checked else st.dim("[ ]")

                    if actual_idx == current:
                        pointer = st.bold_cyan("❯")
                        styled_lbl = (
                            st.bold_cyan(label) if is_checked else st.bold(label)
                        )
                    else:
                        pointer = " "
                        styled_lbl = st.green(label) if is_checked else label

                    prefix = f"  {pointer} {check} "
                    lines.append(
                        fit_line(prefix, styled_lbl, label, desc, max_w, styler=st)
                    )

                # Down indicator if more below
                if scroll_offset + max_visible < len(items):
                    remaining = len(items) - (scroll_offset + max_visible)
                    lines.append(st.dim(f"  ▼ ({remaining} more below...)"))

            # Clear previous frame rows and redraw in-place
            if rendered_lines > 0:
                out.write(f"\033[{rendered_lines}A\r")
            for line in lines:
                out.write(f"\033[2K{line}\r\n")
            out.flush()
            rendered_lines = len(lines)

            key = read_key(raw_text_mode=searching)

            if searching:
                if key == "enter":
                    searching = False
                elif key == "esc":
                    search_query = ""
                    searching = False
                    current = 0
                    scroll_offset = 0
                elif key == "backspace":
                    search_query = search_query[:-1]
                    current = 0
                    scroll_offset = 0
                elif key == "up" and items:
                    current = (current - 1) % len(items)
                elif key == "down" and items:
                    current = (current + 1) % len(items)
                elif key in ("ctrl_c", "ctrl_d"):
                    searching = False
                elif len(key) == 1 and key.isprintable():
                    search_query += key
                    current = 0
                    scroll_offset = 0
                continue

            # Normal navigation mode
            if key in ("up", "k") and items:
                current = (current - 1) % len(items)
            elif key in ("down", "j") and items:
                current = (current + 1) % len(items)
            elif searchable and key == "/":
                searching = True
            elif searchable and key == "backspace" and search_query:
                search_query = search_query[:-1]
                current = 0
                scroll_offset = 0
            elif searchable and key == "esc" and search_query:
                search_query = ""
                current = 0
                scroll_offset = 0
            elif key == "space" and items:
                cur_key = items[current][0]
                if cur_key in selected_keys:
                    selected_keys.remove(cur_key)
                else:
                    selected_keys.add(cur_key)
            elif key == "a" and items:
                visible_keys = {k for k, _, _ in items}
                if visible_keys.issubset(selected_keys):
                    selected_keys -= visible_keys
                else:
                    selected_keys |= visible_keys
            elif key == "enter":
                break
            elif key in ("ctrl_c", "ctrl_d", "q", "esc"):
                if rendered_lines > 0:
                    out.write(f"\033[{rendered_lines}A\r")
                    for _ in range(rendered_lines):
                        out.write("\033[2K\r\n")
                    out.write(f"\033[{rendered_lines}A\r")
                    out.flush()
                out.write("\nAborted.\n")
                out.flush()
                sys.exit(0)

        # Clear interactive frame cleanly and output final choice
        if rendered_lines > 0:
            out.write(f"\033[{rendered_lines}A\r")
            for _ in range(rendered_lines):
                out.write("\033[2K\r\n")
            out.write(f"\033[{rendered_lines}A\r")
            out.flush()

        chosen_labels = [lbl for k, lbl, _ in all_items if k in selected_keys]
        out.write(
            f"{st.badge()} {st.dim(title)} {st.bold_green(f'{len(chosen_labels)} item(s) selected')}\n"
        )
        out.flush()
        return [k for k, _, _ in all_items if k in selected_keys]
    finally:
        out.write("\033[?25h")
        out.flush()
