import io
import time
from prism.spinner import Spinner, spinner_context
from prism.styling import Styler


def test_spinner_non_tty():
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    sp = Spinner("Processing data", styler=st, stream=buf)
    sp.start()
    sp.update("Almost done")
    sp.stop("All finished")

    out = buf.getvalue()
    assert "Processing data" in out
    assert "All finished" in out


def test_spinner_context():
    buf = io.StringIO()
    st = Styler(color_mode="never", stream=buf)

    with spinner_context("Testing context", styler=st, stream=buf):
        pass

    out = buf.getvalue()
    assert "Testing context" in out
