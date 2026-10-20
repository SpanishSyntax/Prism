"""Interactive text prompts, confirmations, and user input utilities."""

from __future__ import annotations

import getpass
import sys
from typing import TextIO

from rime.styling import Styler


def prompt_input(
    message: str,
    default: str = "",
    styler: Styler | None = None,
    allow_empty: bool = True,
    secret: bool = False,
    stream: TextIO | None = None,
) -> str:
    """
    Prompts user for text input with styled badge and default value.
    Handles EOFError and KeyboardInterrupt cleanly.
    """
    st = styler or Styler()
    out = stream or st.stream

    suffix = f" {st.dim(f'[{default}]')}: " if default else ": "
    prompt_str = f"{st.badge()} {st.bold(message)}{suffix}"

    try:
        if secret:
            out.write(prompt_str)
            out.flush()
            val = getpass.getpass("").strip()
        else:
            val = input(prompt_str).strip()

        if not val and default:
            return default
        if not val and not allow_empty:
            while not val:
                val = input(prompt_str).strip()
                if not val and default:
                    return default
        return val
    except (KeyboardInterrupt, EOFError):
        out.write("\n")
        out.flush()
        sys.exit(0)


def confirm_input(
    message: str,
    default: bool = False,
    styler: Styler | None = None,
    stream: TextIO | None = None,
) -> bool:
    """
    Prompts user for a yes/no confirmation with styled badge.
    Defaults to the given default boolean on empty Enter.
    """
    st = styler or Styler()
    out = stream or st.stream

    choices = "Y/n" if default else "y/N"
    suffix = f" {st.dim(f'[{choices}]')}: "
    prompt_str = f"{st.badge()} {st.bold(message)}{suffix}"

    try:
        val = input(prompt_str).strip().lower()
        if not val:
            return default
        return val in ("y", "yes", "true", "1")
    except (KeyboardInterrupt, EOFError):
        out.write("\n")
        out.flush()
        sys.exit(0)
