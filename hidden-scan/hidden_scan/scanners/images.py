from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path
from hidden_scan.model import Finding

PNG_END = b"IEND\xae\x42\x60\x82"
JPG_END = b"\xff\xd9"                             # EOI (End Of Image) — NU SOI \xff\xd8


def trailing_bytes(path: str) -> int:
    """Octeți după marcatorul de final = aCropalypse / poliglot / payload."""
    data = Path(path).read_bytes()
    for marker in (PNG_END, JPG_END):
        idx = data.rfind(marker)
        if idx != -1:
            return len(data) - (idx + len(marker))
    return 0


def _thumbnail_bytes(path: str) -> bytes:
    """Octeții miniaturii EXIF, în memorie (nu scrie pe disc)."""
    safe = str(Path(path).resolve())
    try:
        res = subprocess.run(["exiftool", "-b", "-ThumbnailImage", safe],
                             capture_output=True, timeout=30)
        if res.stdout:
            return res.stdout
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        pass

    # Fallback nativ Pillow (când exiftool nu este instalat)
    try:
        from PIL import Image
        with Image.open(path) as img:
            exif = img.getexif()
            if exif and hasattr(exif, "get_ifd"):
                ifd1 = exif.get_ifd(0x0103)  # IFD1 / Thumbnail
                if ifd1 and 513 in ifd1 and 514 in ifd1:
                    return b"EXIF_IFD1_THUMB"
    except Exception:
        pass
    return b""


def scan(path: str, *, extract_thumb: bool = False,
         out_dir: str | None = None) -> list[Finding]:
    findings: list[Finding] = []

    trailing = trailing_bytes(path)
    if trailing > 0:
        findings.append(Finding(
            scanner="images", category="residual-data", severity="high",
            title=f"{trailing} octeți după marcatorul de final",
            detail="Tipar aCropalypse sau fișier poliglot / payload atașat.",
            evidence=f"{trailing} B după IEND/FFD9"))

    thumb = _thumbnail_bytes(path)
    if thumb:
        note = "Poate arăta imaginea de dinainte de crop/cenzură. Compar-o manual."
        if extract_thumb and thumb != b"EXIF_IFD1_THUMB":
            dest_dir = Path(out_dir or tempfile.mkdtemp(prefix="hiddenscan_"))
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / (Path(path).stem + "_thumb.jpg")
            dest.write_bytes(thumb)
            evidence = str(dest)
        else:
            evidence = f"miniatură EXIF prezentă ({len(thumb)} B); folosește --extract-thumb"
        findings.append(Finding(
            scanner="images", category="residual-data", severity="medium",
            title="Miniatură EXIF prezentă", detail=note,
            evidence=evidence, confidence="probable"))
    return findings
