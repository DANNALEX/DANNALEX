from __future__ import annotations
import re
import zipfile
from hidden_scan.model import Finding

_RUN = re.compile(r"<w:r[ >].*?</w:r>", re.S)
_TEXT = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
_HEADER = re.compile(r"word/header\d*\.xml")
_EXTERNAL = re.compile(r'Target="(https?://[^"]+)"')
_WHITE = re.compile(r'w:color w:val="FFFFFF"', re.I)
_VANISH = re.compile(r"<w:vanish\b([^>]*)/?>")
_VANISH_OFF = re.compile(r'w:val="(?:false|0)"', re.I)
# extragere independentă de ordinea atributelor (OOXML nu o garantează)
_SHEET_TAG = re.compile(r"<sheet\b[^>]*>")
_SHEET_NAME = re.compile(r'name="([^"]+)"')
_SHEET_STATE = re.compile(r'state="(hidden|veryHidden)"')
_TRACK_CHANGES = re.compile(r"<w:(?:ins|del)\b[^>]*w:author=\"([^\"]+)\"")

_MAX_XML_BYTES = 50 * 1024 * 1024  # 50 MB protecție anti-zip-bomb


def scan_docx(path: str) -> list[Finding]:
    findings: list[Finding] = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc = _read(z, "word/document.xml")

        # 1. text marcat Hidden (vanish) — dar NU dacă e dezactivat explicit
        for run in _RUN.findall(doc):
            m = _VANISH.search(run)
            if m and not _VANISH_OFF.search(m.group(1)):
                txt = "".join(_TEXT.findall(run)).strip()
                if txt:
                    findings.append(Finding(
                        scanner="ooxml", category="hidden-text", severity="high",
                        title="Text marcat Hidden (w:vanish)",
                        detail="Text prezent în fișier, invizibil la afișare/tipărire.",
                        evidence=txt[:200]))

        # 2. text alb — semnal SLAB: confidence 'probable'
        if _WHITE.search(doc):
            findings.append(Finding(
                scanner="ooxml", category="hidden-text", severity="low",
                title="Text cu culoare albă (FFFFFF)",
                detail=("Posibil text alb pe fundal alb. Nu se verifică fundalul "
                        "efectiv; confirmă manual. Nu acoperă themeColor/highlight."),
                evidence='w:color w:val="FFFFFF"', confidence="probable"))

        # 3. revizii / Track Changes rămase neacceptate
        authors = sorted(set(_TRACK_CHANGES.findall(doc)))
        if authors:
            findings.append(Finding(
                scanner="ooxml", category="residual-history", severity="medium",
                title="Modificări urmărite (Track Changes) prezente",
                detail="Textul șters/inserat și autorii reviziilor sunt încă în XML.",
                evidence="Autori revizii: " + ", ".join(authors)))

        # 4. filigran vizibil — stă în antete, nu în corpul documentului
        for name in names:
            if _HEADER.match(name):
                h = _read(z, name)
                if any(m in h for m in ("WordArt", "PowerPlusWaterMark", "<v:shape")):
                    findings.append(Finding(
                        scanner="ooxml", category="watermark", severity="info",
                        title=f"Filigran vizibil în {name}",
                        detail="Filigranul e o formă în antet, nu în corpul documentului.",
                        evidence=name))

        # 5. relații externe (șabloane/imagini remote → callback la deschidere)
        for name in names:
            if name.endswith(".rels"):
                for url in _EXTERNAL.findall(_read(z, name)):
                    if "schemas.openxmlformats.org" in url or "purl.org" in url or "w3.org" in url:
                        continue
                    findings.append(Finding(
                        scanner="ooxml", category="active-content", severity="medium",
                        title="Relație externă",
                        detail="Șablon/imagine remote — posibil callback la deschidere.",
                        evidence=url))
    return findings


def scan_xlsx(path: str) -> list[Finding]:
    findings: list[Finding] = []
    with zipfile.ZipFile(path) as z:
        wb = _read(z, "xl/workbook.xml")
    for tag in _SHEET_TAG.findall(wb):
        state_m = _SHEET_STATE.search(tag)
        if not state_m:
            continue
        state = state_m.group(1)
        name_m = _SHEET_NAME.search(tag)
        name = name_m.group(1) if name_m else "(necunoscut)"
        sev = "high" if state == "veryHidden" else "medium"
        findings.append(Finding(
            scanner="ooxml", category="hidden-content", severity=sev,
            title=f"Foaie ascunsă ({state}): {name}",
            detail="veryHidden nu apare nici în meniul Unhide.",
            evidence=f"{name} [{state}]"))
    return findings


def _read(z: zipfile.ZipFile, name: str) -> str:
    try:
        info = z.getinfo(name)
        if info.file_size > _MAX_XML_BYTES:
            return ""
        return z.read(name).decode("utf-8", "ignore")
    except KeyError:
        return ""
