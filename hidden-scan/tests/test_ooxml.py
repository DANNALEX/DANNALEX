from hidden_scan.scanners import ooxml


def test_hidden_text_docx(fixtures):
    cats = {f.category for f in ooxml.scan_docx(str(fixtures / "hidden.docx"))}
    assert "hidden-text" in cats
