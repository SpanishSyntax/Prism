import io
from prism.engine import UI, ui


def test_ui_facade():
    buf = io.StringIO()
    custom_ui = UI(app_name="custom", icon="⚡", stream=buf, color_mode="never")

    assert "custom" in custom_ui.badge()
    assert "⚡" in custom_ui.badge()

    custom_ui.panel("Status", ["All systems operational"], width=60)
    out = buf.getvalue()
    assert "Status" in out
    assert "All systems operational" in out


def test_global_ui_instance():
    assert ui is not None
    assert "🌈" in ui.badge()
    assert callable(ui.panel)
    assert callable(ui.spinner)
    assert callable(ui.select)
    assert callable(ui.multiselect)
