import io
from prism.menus import fit_line, multiselect_menu, normalize_options, select_menu
from prism.styling import Styler


def test_normalize_options():
    raw = [
        "simple",
        ("key1", "label1"),
        ("key2", "label2", "description2"),
    ]
    norm = normalize_options(raw)
    assert norm == [
        ("simple", "simple", ""),
        ("key1", "label1", ""),
        ("key2", "label2", "description2"),
    ]


def test_fit_line():
    st = Styler(color_mode="never")
    line = fit_line("  > ", "Title", "Title", "Some description", max_w=50, styler=st)
    assert "Title" in line
    assert "Some description" in line

    truncated = fit_line("  > ", "Title", "Title", "Super long description " * 5, max_w=20, styler=st)
    assert "..." in truncated


def test_select_menu_non_tty(monkeypatch):
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)
    options = [("opt1", "Option One"), ("opt2", "Option Two")]

    monkeypatch.setattr("builtins.input", lambda _: "2")
    res = select_menu("Choose", options, styler=st, stream=buf)
    assert res == "opt2"


def test_multiselect_menu_non_tty(monkeypatch):
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)
    options = [("a", "Alpha"), ("b", "Beta"), ("c", "Gamma")]

    monkeypatch.setattr("builtins.input", lambda _: "1, 3")
    res = multiselect_menu("Choose multiple", options, styler=st, stream=buf)
    assert res == ["a", "c"]
