"""Unit tests for Prism serve banner and searchbox."""

import io
from prism import UI, render_serve_banner, searchbox
from prism.styling import Styler


def test_render_serve_banner_human():
    out = io.StringIO()
    st = Styler(color_mode="never", agent_mode=False, stream=out)
    render_serve_banner(
        title="🏮 Lantern Live Dev Server",
        url="http://127.0.0.1:8080",
        target="explainer.md",
        details={"Template": "explainer", "Watching": "/workspace"},
        controls=[("[q]", "stop"), ("[r]", "reload")],
        warning="Ephemeral local dev server only.",
        styler=st,
        stream=out,
    )
    val = out.getvalue()
    assert "Lantern Live Dev Server" in val
    assert "http://127.0.0.1:8080" in val
    assert "explainer.md" in val
    assert "Template:" in val
    assert "[q] stop" in val


def test_render_serve_banner_agent_mode():
    out = io.StringIO()
    st = Styler(agent_mode=True, stream=out)
    render_serve_banner(
        title="Lantern Live Dev Server",
        url="http://127.0.0.1:8080",
        target="explainer.md",
        details={"Template": "explainer"},
        styler=st,
        stream=out,
    )
    val = out.getvalue().strip()
    assert val.startswith("SERVER_ACTIVE:")
    assert 'url="http://127.0.0.1:8080"' in val
    assert 'target="explainer.md"' in val
    assert 'template="explainer"' in val
    assert "\033[" not in val
    assert "╭" not in val


def test_searchbox_agent_mode_fallback():
    out = io.StringIO()
    st = Styler(agent_mode=True, stream=out)
    options = [
        ("opt1", "Option One", "First option description"),
        ("opt2", "Option Two", "Second option description"),
    ]
    # Agent mode should return first key without hanging
    chosen = searchbox(
        title="Test Search",
        options=options,
        styler=st,
        stream=out,
    )
    assert chosen == "opt1"


def test_ui_serve_banner_method():
    out = io.StringIO()
    ui = UI(app_name="lantern", color_mode="never", agent_mode=True, stream=out)
    ui.serve_banner(
        title="Test Server",
        url="http://localhost:3000",
    )
    assert 'url="http://localhost:3000"' in out.getvalue()
