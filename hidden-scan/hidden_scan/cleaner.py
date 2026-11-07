from __future__ import annotations
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from hidden_scan.model import CleanResult
from hidden_scan.utils import guess_type
from hidden_scan.scanners.unicode_scan import classify
from hidden_scan.scanners.pdf import RISKY_KEYS

_RUN_RE = re.compile(r"<w:r[ >].*?</w:r>", re.S)
_VANISH_RE = re.compile(r"<w:vanish\b([^>]*)/?>")
_VANISH_OFF_RE = re.compile(r'w:val="(?:false|0)"', re.I)

# Tag-uri OOXML din docProps/core.xml și app.xml care trebuie golite la curățare
_OOXML_SENSITIVE_TAGS = {
    "creator", "lastModifiedBy", "revision", "title", "subject",
    "description", "keywords", "category", "contentStatus",
    "Company", "Manager", "Application", "AppVersion", "TotalTime",
    "Template", "HyperlinkBase",
}

_CLEAN_CORE_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
</cp:coreProperties>"""

_CLEAN_APP_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
</Properties>"""


def default_clean_output_path(src: Path, *, in_place: bool = False,
                              batch_root: Path | None = None) -> Path:
    """Calculează calea fișierului curățat:
    - dacă in_place=True: suprascrie fișierul (cu salvare temporară atomică);
    - dacă face parte dintr-un director scanat în lot (batch_root): scrie în
      batch_root / '_CURATATE' / relative_path;
    - pentru un fișier individual: scrie lângă el cu sufixul '_curat.ext'."""
    if in_place:
        return src
    if batch_root is not None:
        try:
            rel = src.resolve().relative_to(batch_root.resolve())
            dest = batch_root / "_CURATATE" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            return dest
        except ValueError:
            pass
    return src.with_name(f"{src.stem}_curat{src.suffix}")


def clean_pdf(src: Path, dst: Path) -> list[str]:
    """Curăță complet metadatele DocInfo, XMP, atașamentele, acțiunile active
    și istoria incrementală (%%EOF) dintr-un PDF."""
    import pikepdf

    removed: list[str] = []
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with pikepdf.open(src) as pdf:
            # 1. Șterge toate cheile din DocInfo
            if pdf.docinfo:
                keys = [str(k) for k in list(pdf.docinfo.keys())]
                for k in list(pdf.docinfo.keys()):
                    del pdf.docinfo[k]
                if keys:
                    removed.append(f"PDF DocInfo ({', '.join(keys)})")

            try:
                del pdf.trailer["/Info"]
            except KeyError:
                pass

            # 2. Șterge stream-ul XMP /Metadata din Root
            if "/Metadata" in pdf.Root:
                del pdf.Root["/Metadata"]
                removed.append("XMP Metadata stream (/Metadata)")

            # 3. Șterge atașamentele încorporate
            att = getattr(pdf, "attachments", None)
            if att:
                for name in list(att.keys()):
                    del att[name]
                    removed.append(f"Atașament încorporat: {name}")

            # 4. Șterge acțiunile active (/OpenAction, /AA, /JavaScript, /JS)
            seen: set[tuple[int, int]] = set()

            def strip_risky(obj) -> None:
                try:
                    if getattr(obj, "is_indirect", False):
                        gen = obj.objgen
                        if gen in seen:
                            return
                        seen.add(gen)
                    if isinstance(obj, (pikepdf.Dictionary, pikepdf.Stream)):
                        for key in list(obj.keys()):
                            if str(key) in RISKY_KEYS:
                                del obj[key]
                                removed.append(f"Acțiune activă PDF: {key}")
                            else:
                                strip_risky(obj[key])
                    elif isinstance(obj, pikepdf.Array):
                        for item in obj:
                            strip_risky(item)
                except Exception:
                    return

            strip_risky(pdf.Root)

            # 5. Salvează într-un fișier nou (elimină toate update-urile incrementale %%EOF)
            pdf.remove_unreferenced_resources()
            pdf.save(
                tmp_path,
                linearize=False,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
            )

            # Unele versiuni pikepdf re-scriu Producer la save; îl golim explicit dacă a apărut
        with pikepdf.open(tmp_path, allow_overwriting_input=True) as pdf2:
            if "/Info" in pdf2.trailer:
                del pdf2.trailer["/Info"]
            if "/Metadata" in pdf2.Root:
                del pdf2.Root["/Metadata"]
            pdf2.save(tmp_path)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_path), str(dst))
        if not removed:
            removed.append("Structură PDF rescrisă curat (fără reziduuri incrementale)")
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return removed


def clean_ooxml(src: Path, dst: Path, *, remove_hidden_text: bool = True) -> list[str]:
    """Curăță metadatele din .docx / .xlsx / .pptx (docProps/core.xml, app.xml, custom.xml,
    anonimizează autorii comentariilor și, opțional, elimină run-urile w:vanish)."""
    removed: list[str] = []
    with tempfile.NamedTemporaryFile(suffix=src.suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with zipfile.ZipFile(src, "r") as zin, \
             zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == "docProps/core.xml":
                    removed.append("OOXML docProps/core.xml (Autor, Ultima modificare, Revizii, Date)")
                    data = _CLEAN_CORE_XML
                elif item.filename == "docProps/app.xml":
                    removed.append("OOXML docProps/app.xml (Companie, Manager, Timp editare, Aplicație)")
                    data = _CLEAN_APP_XML
                elif item.filename == "docProps/custom.xml":
                    removed.append("OOXML docProps/custom.xml (Proprietăți personalizate)")
                    continue
                elif item.filename == "word/document.xml" and remove_hidden_text:
                    text_xml = data.decode("utf-8", "ignore")
                    cleaned_runs = 0

                    def _strip_vanish_run(match: re.Match) -> str:
                        nonlocal cleaned_runs
                        run_xml = match.group(0)
                        m = _VANISH_RE.search(run_xml)
                        if m and not _VANISH_OFF_RE.search(m.group(1)):
                            cleaned_runs += 1
                            return ""
                        return run_xml

                    new_xml = _RUN_RE.sub(_strip_vanish_run, text_xml)
                    if cleaned_runs > 0:
                        removed.append(f"Text ascuns Word (w:vanish): {cleaned_runs} fragmente eliminate")
                        data = new_xml.encode("utf-8")
                elif item.filename == "word/comments.xml":
                    text_xml = data.decode("utf-8", "ignore")
                    new_xml, n_sub = re.subn(r'w:author="[^"]*"', 'w:author="Anonim"', text_xml)
                    new_xml, _ = re.subn(r'w:initials="[^"]*"', 'w:initials=""', new_xml)
                    if n_sub > 0:
                        removed.append(f"Autori comentarii anonimizați ({n_sub})")
                        data = new_xml.encode("utf-8")

                # Curățăm și timestamp-ul din header-ul ZIP (opțional dar util pentru confidențialitate)
                clean_info = zipfile.ZipInfo(filename=item.filename, date_time=(2026, 1, 1, 0, 0, 0))
                clean_info.compress_type = zipfile.ZIP_DEFLATED
                zout.writestr(clean_info, data)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_path), str(dst))
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return removed


def clean_image(src: Path, dst: Path) -> list[str]:
    """Curăță complet EXIF, GPS, miniatură EXIF, chunk-uri text PNG și octeții
    de după IEND / FFD9 (aCropalypse) prin re-salvare curată din pixeli."""
    from PIL import Image

    removed: list[str] = []
    with tempfile.NamedTemporaryFile(suffix=src.suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with Image.open(src) as img:
            if img.getexif():
                removed.append("EXIF / GPS / Miniatură EXIF")
            if img.info:
                extra_keys = [k for k in img.info.keys()
                              if k not in ("jfif", "jfif_version", "jfif_unit", "jfif_density", "dpi")]
                if extra_keys:
                    removed.append(f"Metadate imagine ({', '.join(extra_keys)})")

            # Construiește o imagine nouă curată doar cu pixelii (fără info/EXIF)
            clean_img = img.copy()
            clean_img.info.clear()
            fmt = img.format or ("PNG" if src.suffix.lower() == ".png" else "JPEG")
            save_kwargs = {}
            if fmt.upper() in ("JPEG", "JPG"):
                if clean_img.mode in ("RGBA", "P"):
                    clean_img = clean_img.convert("RGB")
                save_kwargs["quality"] = 95
                save_kwargs["exif"] = b""
            clean_img.save(tmp_path, format=fmt, **save_kwargs)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_path), str(dst))
        removed.append("Pixeli rescriși curat (fără EXIF și fără octeți după EOF)")
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return removed


def clean_text_file(src: Path, dst: Path) -> list[str]:
    """Elimină toate caracterele Unicode invizibile (tag block, bidi, zero-width,
    variation selectors) dintr-un fișier text."""
    text = src.read_text(encoding="utf-8", errors="ignore")
    kept: list[str] = []
    removed_count = 0
    for ch in text:
        if classify(ord(ch)) is not None:
            removed_count += 1
        else:
            kept.append(ch)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(kept), encoding="utf-8")
    if removed_count > 0:
        return [f"{removed_count} caractere Unicode invizibile eliminate"]
    return ["Fișier text verificat și rescris curat (UTF-8)"]


def clean_file(path: str | Path, *, output_path: str | Path | None = None,
               in_place: bool = False, batch_root: str | Path | None = None) -> CleanResult:
    """Curăță metadatele și conținutul ascuns dintr-un fișier (PDF, DOCX, XLSX,
    Imagini, Text) și returnează un obiect CleanResult."""
    src = Path(path)
    res = CleanResult(source_file=str(src))

    if not src.exists():
        res.errors.append(f"Fișier inexistent: {src}")
        return res

    b_root = Path(batch_root) if batch_root else None
    dst = Path(output_path) if output_path else default_clean_output_path(
        src, in_place=in_place, batch_root=b_root
    )
    res.output_file = str(dst)

    ext = src.suffix.lower()
    ft = guess_type(src)

    try:
        if ft == "application/pdf" or ext == ".pdf":
            res.removed_items = clean_pdf(src, dst)
            res.cleaned = True
        elif ext in (".docx", ".xlsx", ".pptx") or ft == "application/zip":
            res.removed_items = clean_ooxml(src, dst)
            res.cleaned = True
        elif ft.startswith("image/") or ext in (".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"):
            res.removed_items = clean_image(src, dst)
            res.cleaned = True
        else:
            res.removed_items = clean_text_file(src, dst)
            res.cleaned = True
    except Exception as exc:
        res.errors.append(f"Eroare la curățare: {exc}")
        res.cleaned = False

    return res
