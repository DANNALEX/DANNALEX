from __future__ import annotations
import pikepdf
from hidden_scan.model import Finding

# chei de acțiune periculoase; /EmbeddedFile scos (tratat separat via attachments)
HIGH_KEYS = {"/OpenAction", "/Launch", "/JavaScript", "/JS", "/SubmitForm"}
MEDIUM_KEYS = {"/AA", "/URI"}
RISKY_KEYS = HIGH_KEYS | MEDIUM_KEYS

_EOF = b"%%EOF"


def count_eof_markers(path: str, chunk: int = 1 << 20) -> int:
    """Numără %%EOF în chunk-uri (fără a încărca tot fișierul în RAM)."""
    overlap = len(_EOF) - 1
    count, prev = 0, b""
    with open(path, "rb") as f:
        while block := f.read(chunk):
            buf = prev + block
            count += buf.count(_EOF)
            prev = buf[-overlap:]
    return count


def _risky_keys(pdf: pikepdf.Pdf) -> set[str]:
    """Traversează RECURSIV graful de obiecte (Dictionary/Stream/Array) pornind
    din Root, colectând cheile de acțiune oriunde ar fi — inline sau indirecte.
    Dedup pe indirecte (via objgen) previne buclele."""
    found: set[str] = set()
    seen: set[tuple[int, int]] = set()

    def walk(obj) -> None:
        try:
            if getattr(obj, "is_indirect", False):
                gen = obj.objgen
                if gen in seen:
                    return
                seen.add(gen)
            if isinstance(obj, (pikepdf.Dictionary, pikepdf.Stream)):
                for key in obj.keys():
                    if str(key) in RISKY_KEYS:
                        found.add(str(key))
                    walk(obj[key])
            elif isinstance(obj, pikepdf.Array):
                for item in obj:
                    walk(item)
        except Exception:
            return

    walk(pdf.Root)
    return found


def scan(path: str) -> list[Finding]:
    findings: list[Finding] = []

    with pikepdf.open(path) as pdf:
        markers = count_eof_markers(path)
        linearized = bool(getattr(pdf, "is_linearized", False))
        baseline = 2 if linearized else 1
        incremental = max(0, markers - baseline)
        if incremental >= 1:
            findings.append(Finding(
                scanner="pdf", category="residual-history", severity="medium",
                confidence="probable",
                title=f"~{incremental} update(uri) incremental(e) probabil(e)",
                detail=("Versiunile anterioare pot fi recuperabile. Confirmă cu "
                        "qpdf/structura xref — %%EOF poate apărea și în stream-uri."),
                evidence=f"{markers} × %%EOF (linearizat={linearized})"))

        for key in sorted(_risky_keys(pdf)):
            sev = "high" if key in HIGH_KEYS else "medium"
            findings.append(Finding(
                scanner="pdf", category="active-content", severity=sev,
                title=f"Element activ: {key}",
                detail="Cod/acțiune care se poate executa la deschidere.",
                evidence=key))

        for name in list(getattr(pdf, "attachments", {})):
            findings.append(Finding(
                scanner="pdf", category="embedded-file", severity="high",
                title=f"Fișier încorporat: {name}",
                detail="Atașament complet ascuns în PDF.",
                evidence=name))

        try:
            with pdf.open_metadata() as meta:
                if "xmpMM:History" in str(meta):
                    findings.append(Finding(
                        scanner="pdf", category="metadata", severity="medium",
                        title="Istoric de editare XMP (xmpMM:History)",
                        detail="Lanțul instrumentelor de editare, cu timestamps.",
                        evidence="xmpMM:History prezent"))
        except Exception:
            pass
    return findings
