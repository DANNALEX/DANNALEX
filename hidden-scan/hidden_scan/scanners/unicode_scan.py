from __future__ import annotations
import re
import unicodedata as ud
from hidden_scan.model import Finding

_BIDI = {0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069}
_WORD = re.compile(r"\w+", re.UNICODE)
_SCRIPT_PREFIXES = ("LATIN", "CYRILLIC", "GREEK")

# kind -> (severity, confidence)
_KIND_META = {
    "tag block (ASCII smuggling)": ("high", "confirmed"),
    "bidi control":                ("high", "confirmed"),
    "format (Cf)":                 ("medium", "confirmed"),
    "variation selector":          ("medium", "probable"),
    "variation selector suppl.":   ("medium", "probable"),
}


def classify(cp: int) -> str | None:
    ch = chr(cp)
    # întâi intervalele specifice (unele sunt și Cf) ...
    if 0xE0000 <= cp <= 0xE007F:
        return "tag block (ASCII smuggling)"
    if cp in _BIDI:
        return "bidi control"
    if 0xFE00 <= cp <= 0xFE0F:
        return "variation selector"
    if 0xE0100 <= cp <= 0xE01EF:
        return "variation selector suppl."
    # ... apoi restul caracterelor de format (zero-width, BOM etc.)
    if ud.category(ch) == "Cf":
        return "format (Cf)"
    return None


def _script(ch: str) -> str | None:
    name = ud.name(ch, "")
    prefix = name.split(" ", 1)[0] if name else ""
    return prefix if prefix in _SCRIPT_PREFIXES else None


def scan_text(text: str, limit: int = 500) -> list[Finding]:
    findings: list[Finding] = []

    # 1. codepoint-uri invizibile
    for i, ch in enumerate(text):
        kind = classify(ord(ch))
        if kind:
            sev, conf = _KIND_META[kind]
            findings.append(Finding(
                scanner="unicode", category="invisible-unicode",
                severity=sev, confidence=conf,
                title=f"Caracter invizibil: {kind}",
                detail="Codepoint fără reprezentare vizuală în text.",
                evidence=f"poz {i}: U+{ord(ch):04X} ({kind})"))
            if len(findings) >= limit:
                break

    # 2. homoglife: mai multe scripturi în același cuvânt
    for word in _WORD.findall(text):
        scripts = {s for s in (_script(c) for c in word) if s}
        if len(scripts) > 1:
            findings.append(Finding(
                scanner="unicode", category="homoglyph", severity="medium",
                title="Amestec de scripturi în același cuvânt",
                detail="Posibil homoglyph (ex: Latin + Cyrillic).",
                evidence=f"{word!r}: {sorted(scripts)}", confidence="probable"))
    return findings
