from __future__ import annotations
import re
import shutil
from hidden_scan.model import Finding
from hidden_scan.config import INJECTION_MARKERS

_WORD = re.compile(r"[^\W\d_]{3,}", re.UNICODE)


def _bag(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text)}


def scan_pdf(path: str) -> list[Finding]:
    """Compară textul extras (mașină) cu OCR-ul paginii randate (om)."""
    from pdfminer.high_level import extract_text
    from pdf2image import convert_from_path
    import pytesseract

    t_bin = shutil.which("tesseract")
    if t_bin:
        pytesseract.pytesseract.tesseract_cmd = t_bin

    machine = extract_text(path) or ""
    human = "\n".join(pytesseract.image_to_string(img)
                      for img in convert_from_path(path, dpi=200))

    only_machine = _bag(machine) - _bag(human)
    if not only_machine:
        return []

    hits = only_machine & INJECTION_MARKERS
    if hits:
        severity = "high"
        evidence = "markeri: " + ", ".join(sorted(hits))
    else:
        severity = "medium"
        evidence = "sample: " + ", ".join(sorted(only_machine)[:30])

    return [Finding(
        scanner="dual-extraction", category="prompt-injection",
        severity=severity, confidence="probable",
        title=f"{len(only_machine)} cuvinte prezente doar pentru mașină",
        detail=("Text extractibil dar invizibil la randare — semnal de conținut "
                "ascuns / prompt injection. Confirmă manual (poate fi zgomot OCR)."),
        evidence=evidence)]
