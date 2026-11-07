from __future__ import annotations
import argparse
import json
import sys
import webbrowser
from pathlib import Path

from hidden_scan.core import analyze_targets
from hidden_scan.report import render_html


def _configure_utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_console()
    ap = argparse.ArgumentParser(
        prog="hidden-scan",
        description="Detector și curățător de metadate și conținut ascuns în fișiere și directoare.")
    ap.add_argument("files", nargs="+", help="fișiere sau directoare de analizat/curățat")
    ap.add_argument("--clean", action="store_true",
                    help="șterge metadatele și conținutul ascuns (creează copie curată sau în _CURATATE)")
    ap.add_argument("--in-place", action="store_true",
                    help="cu --clean: suprascrie direct fișierele originale")
    ap.add_argument("--no-recursive", action="store_true",
                    help="nu parcurge subdirectoarele când ținta e un director")
    ap.add_argument("--llm", action="store_true",
                    help="activează dual-extraction/OCR (documente pentru LLM)")
    ap.add_argument("--stego", action="store_true",
                    help="activează steganaliza (zsteg) pe imagini")
    ap.add_argument("--extract-thumb", action="store_true",
                    help="scrie miniaturile EXIF într-un director temporar")
    ap.add_argument("--json", metavar="PATH", help="scrie raportul JSON")
    ap.add_argument("--html", metavar="PATH", help="scrie raportul HTML")
    ap.add_argument("--open-html", action="store_true",
                    help="deschide automat raportul HTML în browser")
    ap.add_argument("--fail-on", choices=["MEDIUM", "HIGH"], default=None,
                    help="exit code 2 dacă riscul ≥ prag")
    args = ap.parse_args(argv)

    reports = analyze_targets(
        args.files,
        llm_mode=args.llm,
        stego=args.stego,
        extract_thumb=args.extract_thumb,
        clean=args.clean,
        in_place=args.in_place,
        recursive=not args.no_recursive,
    )
    payload = [r.as_dict() for r in reports]

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    else:
        print(text)

    if args.html:
        html_path = Path(args.html).resolve()
        html_path.write_text(render_html(reports), encoding="utf-8")
        if args.open_html:
            webbrowser.open(html_path.as_uri())

    if args.fail_on and reports:
        order = {"MEDIUM": 1, "HIGH": 2}
        worst = max(order.get(r.risk, 0) for r in reports)
        if worst >= order[args.fail_on]:
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
