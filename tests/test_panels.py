import io
from prism.panels import render_error_panel, render_panel
from prism.styling import Styler
from prism.terminal import strip_ansi


def test_render_panel():
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    render_panel(
        title="DASHBOARD",
        lines=["Line 1", "A longer second line with information"],
        width=50,
        styler=st,
        stream=buf,
    )

    out = buf.getvalue()
    clean = strip_ansi(out)
    assert "╭─ DASHBOARD" in clean
    assert "│ Line 1" in clean
    assert "│ A longer second line with information" in clean
    assert "╰" in clean


def test_render_panel_truncation():
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    super_long = "X" * 100
    render_panel(
        title="NARROW",
        lines=[super_long],
        width=40,
        styler=st,
        stream=buf,
    )

    out = buf.getvalue()
    clean = strip_ansi(out)
    assert "..." in clean


def test_render_error_panel():
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    render_error_panel(
        title="Fatal Error",
        lines=["Failed to compile LaTeX"],
        styler=st,
        stream=buf,
    )

    out = buf.getvalue()
    clean = strip_ansi(out)
    assert "Fatal Error" in clean
    assert "Failed to compile LaTeX" in clean
