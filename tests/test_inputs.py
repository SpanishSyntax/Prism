import io
from prism.inputs import confirm_input, prompt_input
from prism.styling import Styler


def test_prompt_input_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    val = prompt_input("Enter value", default="fallback", styler=st, stream=buf)
    assert val == "fallback"


def test_prompt_input_value(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "custom_value")
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    val = prompt_input("Enter value", default="fallback", styler=st, stream=buf)
    assert val == "custom_value"


def test_confirm_input(monkeypatch):
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    monkeypatch.setattr("builtins.input", lambda _: "")
    assert confirm_input("Proceed?", default=True, styler=st, stream=buf) is True
    assert confirm_input("Proceed?", default=False, styler=st, stream=buf) is False

    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert confirm_input("Proceed?", default=False, styler=st, stream=buf) is True

    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert confirm_input("Proceed?", default=True, styler=st, stream=buf) is False
