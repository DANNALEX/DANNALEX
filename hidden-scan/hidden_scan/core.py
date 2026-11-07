from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

from hidden_scan.model import Finding, Report
from hidden_scan.utils import (
    sha256, guess_type, tool_version, read_text_best_effort, collect_target_files,
)
from hidden_scan.config import RISK_WEIGHTS, RISK_THRESHOLDS
from hidden_scan.scanners import (
    metadata, ooxml, pdf, images, unicode_scan, dual_extraction, external,
)
from hidden_scan.cleaner import clean_file

_TEXT_EXT = {".txt", ".md", ".csv", ".json", ".py", ".js", ".ts", ".yaml", ".yml"}


def analyze(path: str | Path, *, llm_mode: bool = False, stego: bool = False,
            extract_thumb: bool = False, clean: bool = False,
            in_place: bool = False, batch_root: str | Path | None = None) -> Report:
    p = Path(path)
    report = Report(file=str(p),
                    analyzed_at=datetime.now(timezone.utc).isoformat())

    # I/O de bază protejat — fișier lipsă/necitibil → eroare, nu traceback
    try:
        report.sha256 = sha256(p)
        report.size_bytes = p.stat().st_size
        report.filetype = guess_type(p)
    except OSError as exc:
        report.errors.append(f"acces fișier: {exc}")
        return report

    report.tool_versions = {
        "exiftool": tool_version("exiftool"),
        "qpdf": tool_version("qpdf", "--version"),
        "tesseract": tool_version("tesseract", "--version"),
    }

    def run(fn, *args, **kwargs):
        try:
            report.findings.extend(fn(*args, **kwargs))
        except Exception as exc:  # scanerele nu opresc pipeline-ul
            report.errors.append(f"{fn.__module__}.{fn.__name__}: {exc}")

    ext = p.suffix.lower()
    ft = report.filetype

    # --- ieftin: metadate (întotdeauna) ---
    run(metadata.scan, str(p))

    # --- pe tip de fișier ---
    if ext == ".docx":
        run(ooxml.scan_docx, str(p))
    elif ext == ".xlsx":
        run(ooxml.scan_xlsx, str(p))
    elif ft == "application/pdf" or ext == ".pdf":
        run(pdf.scan, str(p))
        if llm_mode:  # scump: OCR doar când documentul e destinat unui LLM
            run(dual_extraction.scan_pdf, str(p))
            run(external.phantomlint, str(p))
    elif ft.startswith("image/"):
        run(images.scan, str(p), extract_thumb=extract_thumb)
        if stego:
            run(external.zsteg, str(p))

    # --- Unicode pe orice text extractibil (text/cod) ---
    if ft.startswith("text/") or ext in _TEXT_EXT:
        run(unicode_scan.scan_text, read_text_best_effort(p))

    report.risk = _score(report.findings)

    # --- Opțional: Ștergere metadate / curățare + verificare post-curățare ---
    if clean:
        c_res = clean_file(p, in_place=in_place, batch_root=batch_root)
        c_res.before_findings_count = len(report.findings)
        if c_res.cleaned and Path(c_res.output_file).exists():
            after_rep = analyze(c_res.output_file, llm_mode=False, stego=False,
                                extract_thumb=False, clean=False)
            c_res.after_findings_count = len(after_rep.findings)
        report.clean_result = c_res

    return report


def analyze_targets(targets: list[str | Path], *, llm_mode: bool = False,
                    stego: bool = False, extract_thumb: bool = False,
                    clean: bool = False, in_place: bool = False,
                    recursive: bool = True) -> list[Report]:
    """Analizează și (opțional) curăță o listă de fișiere și/sau directoare."""
    reports: list[Report] = []
    for t in targets:
        tp = Path(t)
        batch_root = tp if tp.exists() and tp.is_dir() else None
        files = collect_target_files([tp], recursive=recursive)
        for f in files:
            reports.append(analyze(
                f,
                llm_mode=llm_mode,
                stego=stego,
                extract_thumb=extract_thumb,
                clean=clean,
                in_place=in_place,
                batch_root=batch_root,
            ))
    return reports


def _score(findings: list[Finding]) -> str:
    total = 0.0
    for f in findings:
        w = RISK_WEIGHTS[f.severity]
        if f.confidence == "probable":
            w *= 0.5
        total += w
    if total >= RISK_THRESHOLDS["high"]:
        return "HIGH"
    if total >= RISK_THRESHOLDS["medium"]:
        return "MEDIUM"
    return "LOW"
