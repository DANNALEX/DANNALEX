from __future__ import annotations
import hashlib
import mimetypes
import os
import shutil
import subprocess
from pathlib import Path

from hidden_scan.config import SUPPORTED_EXTENSIONS, IGNORED_DIRS

# Căi standard Windows pentru uneltele externe (când aplicația e pornită din Explorer)
_WIN_EXTRA_PATHS = [
    r"C:\Program Files\Tesseract-OCR",
    r"C:\poppler\Library\bin",
    r"C:\Program Files\qpdf\bin",
    r"C:\ProgramData\chocolatey\bin",
]

for _p in _WIN_EXTRA_PATHS:
    if os.path.isdir(_p) and _p.lower() not in os.environ.get("PATH", "").lower():
        os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")

# Semnături magice — verificate ÎNAINTEA extensiei
_MAGIC = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"PK\x03\x04": "application/zip",   # și OOXML/ODF (container ZIP)
}


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_type(path: str | Path) -> str:
    """Tipul MIME după semnătura magică întâi, apoi după extensie."""
    with open(path, "rb") as f:
        head = f.read(12)
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "image/webp"
    for sig, mime in _MAGIC.items():
        if head.startswith(sig):
            return mime
    kind, _ = mimetypes.guess_type(str(path))
    return kind or "application/octet-stream"


def tool_version(binary: str, arg: str = "-ver") -> str:
    """Versiunea unei unelte CLI, pentru trasabilitatea raportului."""
    resolved = shutil.which(binary)
    if not resolved:
        return "absent"
    try:
        out = subprocess.run([resolved, arg], capture_output=True,
                             text=True, timeout=10)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except (subprocess.SubprocessError, IndexError, OSError):
        return "necunoscut"


def read_text_best_effort(path: str | Path) -> str:
    """Text brut pentru scanarea Unicode, când fișierul e text/cod."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except (OSError, ValueError):
        return ""


def collect_target_files(targets: list[str | Path], recursive: bool = True) -> list[Path]:
    """Expandează o listă de fișiere și/sau directoare în lista de fișiere eligibile.
    Ignoră automat fișierele temporare Office (~$*) și directoarele de output (_CURATATE)."""
    result: list[Path] = []
    seen: set[Path] = set()

    for t in targets:
        p = Path(t)
        if not p.exists():
            result.append(p)
            continue

        if p.is_file():
            if p.name.startswith("~$"):
                continue
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                result.append(p)
        elif p.is_dir():
            iterator = p.rglob("*") if recursive else p.glob("*")
            for child in sorted(iterator):
                if not child.is_file():
                    continue
                if child.name.startswith("~$"):
                    continue
                if any(part in IGNORED_DIRS for part in child.parts):
                    continue
                if child.stem.endswith("_curat"):
                    continue
                if child.suffix.lower() in SUPPORTED_EXTENSIONS:
                    resolved = child.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        result.append(child)
    return result
