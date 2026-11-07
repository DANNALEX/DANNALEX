from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from hidden_scan.model import Finding


def phantomlint(path: str, timeout: int = 300) -> list[Finding]:
    """Wrapper best-effort peste PhantomLint (arXiv:2508.17884)."""
    if not shutil.which("phantomlint"):
        return []
    safe = str(Path(path).resolve())
    try:
        res = subprocess.run(["phantomlint", safe],
                             capture_output=True, text=True, timeout=timeout)
    except subprocess.SubprocessError as exc:
        return [Finding(scanner="phantomlint", category="tool-error",
                        severity="info", title="PhantomLint a eșuat",
                        detail=str(exc), confidence="probable")]

    if res.returncode == 0:
        return []
    if res.returncode == 1:
        return [Finding(
            scanner="phantomlint", category="prompt-injection", severity="high",
            title="PhantomLint a semnalat prompt ascuns",
            detail="Detecție dual-extraction principială.",
            evidence=(res.stdout or res.stderr)[:400])]
    return [Finding(
        scanner="phantomlint", category="tool-error", severity="info",
        title=f"PhantomLint exit {res.returncode}",
        detail="Cod de ieșire neașteptat — verifică interfața reală a uneltei.",
        evidence=(res.stderr or res.stdout)[:300], confidence="probable")]


def zsteg(path: str, timeout: int = 120) -> list[Finding]:
    """LSB pe PNG/BMP. Zgomotos — findings marcate 'probable'."""
    if not shutil.which("zsteg"):
        return []
    safe = str(Path(path).resolve())
    try:
        res = subprocess.run(["zsteg", "-a", safe],
                             capture_output=True, text=True, timeout=timeout)
    except subprocess.SubprocessError:
        return []
    hits = [ln for ln in res.stdout.splitlines()
            if "text" in ln.lower() or "file:" in ln.lower()]
    if hits:
        return [Finding(
            scanner="zsteg", category="steganography", severity="low",
            title=f"zsteg: {len(hits)} candidați LSB",
            detail="Semnal slab — confirmă manual pe planurile de biți.",
            evidence="\n".join(hits[:10]), confidence="probable")]
    return []
