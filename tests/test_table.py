"""Unit tests for Prism table rendering engine."""

import io
from prism import UI, render_table
from prism.styling import Styler


def test_render_table_rounded():
    headers = ["Name", "Status", "Description"]
    rows = [
        ["ls", "active", "List directory contents"],
        ["cat", "active", "Print file contents"],
    ]
    out = io.StringIO()
    st = Styler(color_mode="never", agent_mode=False, stream=out)
    table_str = render_table(
        headers=headers,
        rows=rows,
        style="rounded",
        styler=st,
        stream=out,
    )

    assert "╭" in table_str
    assert "╰" in table_str
    assert "│" in table_str
    assert "ls" in table_str
    assert "active" in table_str
    assert "List directory contents" in table_str


def test_render_table_clean():
    headers = ["Key", "Val"]
    rows = [["a", "1"], ["b", "2"]]
    out = io.StringIO()
    st = Styler(color_mode="never", agent_mode=False, stream=out)
    table_str = render_table(
        headers=headers,
        rows=rows,
        style="clean",
        styler=st,
        stream=out,
    )

    assert "Key" in table_str
    assert "Val" in table_str
    assert "─" in table_str
    assert "╭" not in table_str


def test_render_table_agent_mode_zero_waste():
    headers = ["Role", "Pack", "Description"]
    rows = [
        ["git_status", "git", "Show repo status"],
        ["ls", "fs", "List files"],
    ]
    out = io.StringIO()
    # Agent mode: Zero box-drawing characters, zero ANSI codes
    st = Styler(agent_mode=True, stream=out)
    table_str = render_table(
        headers=headers,
        rows=rows,
        title="Active Tools",
        styler=st,
        stream=out,
    )

    # Must contain title tag
    assert "[Active Tools]" in table_str
    # Must contain headers and content
    assert "Role" in table_str
    assert "git_status" in table_str
    assert "ls" in table_str
    # Must NOT contain decorative Unicode box characters
    assert "╭" not in table_str
    assert "╰" not in table_str
    assert "│" not in table_str
    assert "\033[" not in table_str


def test_ui_table_method():
    ui = UI(app_name="test", color_mode="never", agent_mode=False)
    res = ui.table(
        headers=["Col1", "Col2"],
        rows=[["val1", "val2"]],
        style="rounded",
    )
    assert "Col1" in res
    assert "val1" in res
