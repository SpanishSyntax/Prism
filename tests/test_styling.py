import io
from rime.styling import Styler, detect_color_support


def test_detect_color_support(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert detect_color_support() is False

    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert detect_color_support() is True

    assert detect_color_support(mode="never") is False
    assert detect_color_support(mode="always") is True


def test_styler_formatting():
    buf = io.StringIO()
    st = Styler(app_name="iceberg", icon="❄️", badge_color="1;34", color_mode="always", stream=buf)

    assert "iceberg" in st.badge()
    assert "❄️" in st.badge()

    bold_txt = st.bold("Hello")
    assert "\033[1mHello\033[0m" == bold_txt

    cyan_txt = st.cyan("Blue/Green")
    assert "\033[0;36mBlue/Green\033[0m" == cyan_txt


def test_styler_outputs():
    buf = io.StringIO()
    st = Styler(app_name="test", color_mode="never", stream=buf)

    st.success("Finished task")
    st.info("Information message")
    st.warn("Attention needed")
    st.action("Building derivation")

    output = buf.getvalue()
    assert "✔ Finished task" in output
    assert "ℹ️ Information message" in output
    assert "⚠️ Attention needed" in output
    assert "⚡ Building derivation" in output
