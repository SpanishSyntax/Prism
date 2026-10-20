import re
from rime.terminal import get_terminal_columns, get_terminal_size, strip_ansi, visual_len


def test_strip_ansi():
    text = "\033[1;36mHello World\033[0m"
    assert strip_ansi(text) == "Hello World"
    assert strip_ansi("Plain text") == "Plain text"
    assert strip_ansi("\033[0m") == ""


def test_visual_len():
    text = "\033[1;32mTest\033[0m"
    assert visual_len(text) == 4
    assert visual_len("Normal") == 6


def test_get_terminal_columns_and_size():
    cols = get_terminal_columns(fallback=90)
    assert isinstance(cols, int)
    assert cols > 0

    c, l = get_terminal_size(fallback=(85, 30))
    assert isinstance(c, int)
    assert isinstance(l, int)
    assert c > 0
    assert l > 0
