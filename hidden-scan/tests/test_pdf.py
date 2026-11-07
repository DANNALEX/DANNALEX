import pikepdf
from hidden_scan.scanners import pdf


def test_openaction_detected(tmp_path):
    doc = pikepdf.Pdf.new()
    doc.add_blank_page()
    doc.Root.OpenAction = pikepdf.Dictionary(
        S=pikepdf.Name("/JavaScript"), JS=pikepdf.String("app.alert(1)"))
    out = tmp_path / "js.pdf"
    doc.save(out)
    cats = {f.category for f in pdf.scan(str(out))}
    assert "active-content" in cats


def test_fake_redaction_text_recoverable(fixtures):
    from pdfminer.high_level import extract_text
    txt = extract_text(str(fixtures / "fake_redaction.pdf"))
    assert "AGENT REDACTAT" in txt


def test_clean_pdf_not_flagged_incremental(tmp_path):
    doc = pikepdf.Pdf.new()
    doc.add_blank_page()
    out = tmp_path / "clean.pdf"
    doc.save(out)
    cats = {f.category for f in pdf.scan(str(out))}
    assert "residual-history" not in cats
