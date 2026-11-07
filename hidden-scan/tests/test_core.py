import shutil
import pikepdf
from hidden_scan.core import analyze, analyze_targets


def test_missing_file_records_error_not_traceback():
    r = analyze("nu_exista_9f3a1.pdf")
    assert r.errors and r.risk == "LOW"


def test_docx_routed_and_hashed_end_to_end(fixtures):
    r = analyze(str(fixtures / "hidden.docx"))
    assert r.sha256 and r.filetype
    cats = {f.category for f in r.findings}
    assert "hidden-text" in cats
    assert "metadata" in cats


def test_clean_docx_removes_metadata_and_hidden_text(fixtures, tmp_path):
    src = tmp_path / "doc_compromis.docx"
    shutil.copy2(fixtures / "hidden.docx", src)

    rep = analyze(src, clean=True)
    assert rep.clean_result is not None
    assert rep.clean_result.cleaned
    assert rep.clean_result.before_findings_count >= 2
    assert rep.clean_result.after_findings_count == 0


def test_clean_pdf_removes_metadata_and_active_content(tmp_path):
    src = tmp_path / "dirty.pdf"
    doc = pikepdf.Pdf.new()
    doc.add_blank_page()
    doc.docinfo["/Author"] = "Secret Author"
    doc.docinfo["/Creator"] = "Secret Creator"
    doc.Root.OpenAction = pikepdf.Dictionary(
        S=pikepdf.Name("/JavaScript"), JS=pikepdf.String("app.alert(1)")
    )
    doc.save(src)

    rep = analyze(src, clean=True)
    assert rep.clean_result is not None
    assert rep.clean_result.cleaned
    assert rep.clean_result.before_findings_count >= 2
    assert rep.clean_result.after_findings_count == 0


def test_clean_image_removes_exif_and_trailing_bytes(fixtures, tmp_path):
    src_png = tmp_path / "dirty.png"
    shutil.copy2(fixtures / "acropalypse.png", src_png)
    rep_png = analyze(src_png, clean=True)
    assert rep_png.clean_result is not None and rep_png.clean_result.cleaned
    assert rep_png.clean_result.after_findings_count == 0

    src_jpg = tmp_path / "dirty.jpg"
    shutil.copy2(fixtures / "trailing.jpg", src_jpg)
    rep_jpg = analyze(src_jpg, clean=True)
    assert rep_jpg.clean_result is not None and rep_jpg.clean_result.cleaned
    assert rep_jpg.clean_result.after_findings_count == 0


def test_directory_batch_clean_creates_curatate_subfolder(fixtures, tmp_path):
    batch_dir = tmp_path / "lot_documente"
    batch_dir.mkdir()
    shutil.copy2(fixtures / "hidden.docx", batch_dir / "a.docx")
    shutil.copy2(fixtures / "trailing.jpg", batch_dir / "b.jpg")
    # Fișier temporar Office (~$) care trebuie ignorat automat
    (batch_dir / "~$a.docx").write_bytes(b"corrupt_lock_file")

    reps = analyze_targets([batch_dir], clean=True)
    assert len(reps) == 2
    assert all(r.clean_result and r.clean_result.cleaned for r in reps)
    assert (batch_dir / "_CURATATE" / "a.docx").exists()
    assert (batch_dir / "_CURATATE" / "b.jpg").exists()
    assert all(r.clean_result.after_findings_count == 0 for r in reps)
