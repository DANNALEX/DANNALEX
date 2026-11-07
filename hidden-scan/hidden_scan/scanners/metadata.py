from __future__ import annotations
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from hidden_scan.model import Finding
from hidden_scan.config import META_HIGH, META_MEDIUM, META_LOW
from hidden_scan.utils import guess_type

# xmpMM:History e raportat separat, PDF-specific, de pdf.scan — nu-l dubla aici
_SKIP = ("xmpMM:History",)


def _tier(key: str) -> tuple[str, str] | None:
    """(severity, confidence) după nivelul cheii, sau None dacă nu e sensibilă."""
    k = key.lower()
    if any(s.lower() in k for s in META_HIGH):
        return ("high", "confirmed")
    if any(s.lower() in k for s in META_MEDIUM):
        return ("medium", "confirmed")
    if any(s.lower() in k for s in META_LOW):
        return ("low", "probable")
    return None


def _extract_native_pdf_meta(path: str) -> dict[str, str]:
    import pikepdf
    meta: dict[str, str] = {}
    try:
        with pikepdf.open(path) as pdf:
            if pdf.docinfo:
                for k, v in pdf.docinfo.items():
                    clean_k = str(k).lstrip("/")
                    val = str(v).strip()
                    if val:
                        meta[f"PDF:{clean_k}"] = val
            try:
                with pdf.open_metadata() as xmp:
                    for k, v in xmp.items():
                        val = str(v).strip()
                        if val:
                            meta[f"XMP:{k}"] = val
            except Exception:
                pass
    except Exception:
        pass
    return meta


def _extract_native_ooxml_meta(path: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    try:
        with zipfile.ZipFile(path, "r") as z:
            for prop_file in ("docProps/core.xml", "docProps/app.xml", "docProps/custom.xml"):
                if prop_file not in z.namelist():
                    continue
                raw = z.read(prop_file)
                root = ET.fromstring(raw)
                for elem in root.iter():
                    if elem is root:
                        continue
                    tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                    text = (elem.text or "").strip()
                    if text and text not in ("0", "false", "normal.dotm"):
                        meta[f"OOXML:{tag}"] = text
            # Verifică și autori în word/comments.xml
            if "word/comments.xml" in z.namelist():
                raw_c = z.read("word/comments.xml")
                root_c = ET.fromstring(raw_c)
                authors = set()
                for elem in root_c.iter():
                    for attr_k, attr_v in elem.attrib.items():
                        if attr_k.endswith("author") and attr_v.strip():
                            authors.add(attr_v.strip())
                if authors:
                    meta["OOXML:CommentsAuthor"] = ", ".join(sorted(authors))
    except Exception:
        pass
    return meta


def _extract_native_image_meta(path: str) -> dict[str, str]:
    from PIL import Image, ExifTags
    meta: dict[str, str] = {}
    try:
        with Image.open(path) as img:
            # 1. EXIF standard (JPEG / TIFF / WebP / PNG)
            exif = img.getexif()
            if exif:
                for tag_id, val in exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
                    if tag_name == "GPSInfo":
                        gps_ifd = exif.get_ifd(0x8825)
                        if gps_ifd:
                            meta["EXIF:GPSInfo"] = str(dict(gps_ifd))[:200]
                        elif val:
                            meta["EXIF:GPSInfo"] = str(val)[:200]
                    elif val is not None and str(val).strip():
                        meta[f"EXIF:{tag_name}"] = str(val).strip()[:200]
            # 2. Info dictionary (PNG tEXt/iTXt/zTXt, XMP, Software, Author etc.)
            for k, v in (img.info or {}).items():
                if k in ("exif", "icc_profile", "dpi", "jfif", "jfif_version",
                         "jfif_unit", "jfif_density", "progression", "gamma"):
                    continue
                if isinstance(v, (str, bytes)):
                    val_str = v.decode("utf-8", "ignore") if isinstance(v, bytes) else v
                    if val_str.strip():
                        meta[f"IMG:{k}"] = val_str.strip()[:200]
    except Exception:
        pass
    return meta


def scan(path: str) -> list[Finding]:
    findings: list[Finding] = []
    meta: dict[str, str] = {}

    # 1. Dacă exiftool e instalat pe sistem, îl folosim (acoperire maximă)
    if shutil.which("exiftool"):
        try:
            import exiftool
            with exiftool.ExifToolHelper(common_args=["-a", "-u", "-G1"]) as et:
                raw_meta = et.get_metadata(path)[0]
                for k, v in raw_meta.items():
                    meta[k] = str(v)
        except Exception:
            pass

    # 2. Extracție nativă Python (funcționează 100% fără exiftool instalat)
    p = Path(path)
    ext = p.suffix.lower()
    ft = guess_type(p)

    if ft == "application/pdf" or ext == ".pdf":
        for k, v in _extract_native_pdf_meta(path).items():
            meta.setdefault(k, v)
    elif ft == "application/zip" or ext in (".docx", ".xlsx", ".pptx"):
        for k, v in _extract_native_ooxml_meta(path).items():
            meta.setdefault(k, v)
    elif ft.startswith("image/") or ext in (".png", ".jpg", ".jpeg", ".webp", ".tiff"):
        for k, v in _extract_native_image_meta(path).items():
            meta.setdefault(k, v)

    seen_keys: set[str] = set()
    for key, value in meta.items():
        if any(s in key for s in _SKIP):
            continue
        tier = _tier(key)
        if tier:
            norm_key = key.split(":")[-1].lower()
            if norm_key in seen_keys:
                continue
            seen_keys.add(norm_key)
            sev, conf = tier
            findings.append(Finding(
                scanner="metadata", category="metadata", severity=sev,
                confidence=conf,
                title=f"Metadată sensibilă: {key}",
                detail="Câmp care poate scurge identitate, locație sau istoric.",
                evidence=f"{key} = {str(value)[:200]}",
            ))
    return findings
