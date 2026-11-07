from __future__ import annotations
import argparse
import os
import subprocess
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

from hidden_scan.core import analyze_targets
from hidden_scan.model import Report
from hidden_scan.report import render_html


def _open_in_explorer(path: Path) -> None:
    try:
        if sys.platform.startswith("win"):
            if path.is_dir():
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["explorer.exe", f"/select,{path.resolve()}"])
        else:
            webbrowser.open(path.parent.as_uri())
    except Exception:
        pass


def run_gui(initial_targets: list[str] | None = None,
            auto_action: str | None = None,
            in_place: bool = False) -> int:
    try:
        import customtkinter as ctk
        from tkinter import filedialog, messagebox
    except ImportError:
        # Fallback în linie de comandă dacă tkinter nu este disponibil
        from hidden_scan.cli import main as cli_main
        cli_args = list(initial_targets or [])
        if auto_action == "clean":
            cli_args.append("--clean")
        if in_place:
            cli_args.append("--in-place")
        return cli_main(cli_args)

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("hidden-scan v3.0 — Scanare și Ștergere Metadate (Fișiere & Directoare)")
    app.geometry("980x680")
    app.minsize(820, 540)

    state: dict[str, list[str] | list[Report]] = {
        "targets": [str(Path(t).resolve()) for t in (initial_targets or [])],
        "reports": [],
    }

    # --- Top Bar ---
    top = ctk.CTkFrame(app, corner_radius=8)
    top.pack(fill="x", padx=14, pady=(14, 8))

    title_lbl = ctk.CTkLabel(
        top,
        text="Detector și Curățător de Metadate & Conținut Ascuns (PDF, Word, Excel, Imagini, Text)",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    title_lbl.pack(anchor="w", padx=12, pady=(10, 4))

    target_var = ctk.StringVar(
        value="; ".join(state["targets"]) if state["targets"] else "Niciun fișier sau director selectat."
    )
    target_lbl = ctk.CTkLabel(
        top, textvariable=target_var, text_color=("gray30", "gray75"),
        wraplength=920, justify="left"
    )
    target_lbl.pack(anchor="w", padx=12, pady=(0, 10))

    # --- Controls Bar ---
    ctrl = ctk.CTkFrame(app, corner_radius=8)
    ctrl.pack(fill="x", padx=14, pady=6)

    in_place_var = ctk.BooleanVar(value=in_place)
    recursive_var = ctk.BooleanVar(value=True)
    llm_var = ctk.BooleanVar(value=False)

    def select_files() -> None:
        files = filedialog.askopenfilenames(
            title="Selectează fișiere pentru scanare / ștergere metadate",
            filetypes=[
                ("Toate fișierele suportate", "*.pdf *.docx *.xlsx *.pptx *.jpg *.jpeg *.png *.webp *.txt *.md *.csv *.json *.py"),
                ("Documente PDF/Office", "*.pdf *.docx *.xlsx *.pptx"),
                ("Imagini", "*.jpg *.jpeg *.png *.webp *.tiff *.bmp"),
                ("Toate fișierele", "*.*"),
            ],
        )
        if files:
            state["targets"] = list(files)
            target_var.set("; ".join(state["targets"]))

    def select_folder() -> None:
        folder = filedialog.askdirectory(title="Selectează directorul pentru scanare / ștergere metadate")
        if folder:
            state["targets"] = [folder]
            target_var.set(folder)

    btn_file = ctk.CTkButton(ctrl, text="Alege Fișiere...", width=135, command=select_files)
    btn_file.pack(side="left", padx=(10, 6), pady=10)

    btn_dir = ctk.CTkButton(ctrl, text="Alege Director...", width=135, command=select_folder)
    btn_dir.pack(side="left", padx=6, pady=10)

    chk_rec = ctk.CTkCheckBox(ctrl, text="Inclusiv subdirectoare", variable=recursive_var)
    chk_rec.pack(side="left", padx=10, pady=10)

    chk_inplace = ctk.CTkCheckBox(
        ctrl,
        text="Suprascrie originalul (fără copie _curat / _CURATATE)",
        variable=in_place_var,
    )
    chk_inplace.pack(side="left", padx=10, pady=10)

    chk_llm = ctk.CTkCheckBox(ctrl, text="Dual-Extraction OCR (PDF)", variable=llm_var)
    chk_llm.pack(side="left", padx=10, pady=10)

    # --- Action Buttons ---
    act = ctk.CTkFrame(app, corner_radius=8)
    act.pack(fill="x", padx=14, pady=6)

    status_var = ctk.StringVar(value="Pregătit.")

    log_box = ctk.CTkTextbox(app, font=ctk.CTkFont(family="Consolas", size=13), wrap="word")
    log_box.pack(fill="both", expand=True, padx=14, pady=(6, 10))

    def append_log(msg: str) -> None:
        log_box.configure(state="normal")
        log_box.insert("end", msg + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    def clear_log() -> None:
        log_box.configure(state="normal")
        log_box.delete("1.0", "end")
        log_box.configure(state="disabled")

    def format_reports_to_log(reports: list[Report], cleaned_mode: bool) -> None:
        clear_log()
        if not reports:
            append_log("Nu s-au găsit fișiere eligibile în ținta selectată.")
            return

        high_c = sum(1 for r in reports if r.risk == "HIGH")
        med_c = sum(1 for r in reports if r.risk == "MEDIUM")
        low_c = sum(1 for r in reports if r.risk == "LOW")
        cleaned_c = sum(1 for r in reports if r.clean_result and r.clean_result.cleaned)

        append_log("=" * 86)
        if cleaned_mode:
            append_log(f"REZUMAT ȘTERGERE METADATE: {cleaned_c}/{len(reports)} fișiere curățate cu succes")
        else:
            append_log(f"REZUMAT SCANARE: {len(reports)} fișiere analizate | HIGH: {high_c} | MEDIUM: {med_c} | LOW: {low_c}")
        append_log("=" * 86 + "\n")

        for idx, r in enumerate(reports, 1):
            append_log(f"[{idx}] FIȘIER: {r.file}")
            append_log(f"    Tip: {r.filetype} | Mărime: {r.size_bytes} B | Risc inițial: {r.risk}")
            if r.findings:
                append_log(f"    Constatări detectate ({len(r.findings)}):")
                for f in r.findings:
                    conf_str = " (probabil)" if f.confidence == "probable" else ""
                    append_log(f"      - [{f.severity.upper()}{conf_str}] {f.title} -> {f.evidence}")
            else:
                append_log("    Constatări detectate: 0 (Nicio metadată sensibilă sau conținut ascuns detectat)")

            if r.clean_result:
                cr = r.clean_result
                if cr.cleaned:
                    append_log(f"    >>> [CURĂȚAT CU SUCCES] Salvat în: {cr.output_file}")
                    append_log(f"        Elemente eliminate: {', '.join(cr.removed_items)}")
                    append_log(f"        Verificare după ștergere: {cr.before_findings_count} constatări înainte -> {cr.after_findings_count} după curățare")
                else:
                    append_log(f"    >>> [EROARE LA CURĂȚARE]: {'; '.join(cr.errors)}")
            if r.errors:
                append_log(f"    [!] Erori scaner: {'; '.join(r.errors)}")
            append_log("-" * 86)

    def run_worker(clean_mode: bool) -> None:
        targets = list(state["targets"])
        if not targets:
            messagebox.showwarning("Atenție", "Selectează mai întâi un fișier sau un director!")
            return

        btn_scan.configure(state="disabled")
        btn_clean.configure(state="disabled")
        status_var.set("Se procesează fișierele... Te rugăm să aștepți.")
        clear_log()
        append_log("Procesare în curs...\n")

        def task() -> None:
            try:
                reps = analyze_targets(
                    targets,
                    llm_mode=bool(llm_var.get()),
                    clean=clean_mode,
                    in_place=bool(in_place_var.get()),
                    recursive=bool(recursive_var.get()),
                )
                state["reports"] = reps

                def on_done() -> None:
                    format_reports_to_log(reps, cleaned_mode=clean_mode)
                    btn_scan.configure(state="normal")
                    btn_clean.configure(state="normal")
                    if clean_mode:
                        ok_count = sum(1 for r in reps if r.clean_result and r.clean_result.cleaned)
                        status_var.set(f"Finalizat: {ok_count}/{len(reps)} fișiere curățate de metadate.")
                    else:
                        total_f = sum(len(r.findings) for r in reps)
                        status_var.set(f"Scanare finalizată: {len(reps)} fișiere, {total_f} constatări găsite.")

                app.after(0, on_done)
            except Exception as exc:
                def on_err() -> None:
                    append_log(f"Eroare neașteptată: {exc}")
                    btn_scan.configure(state="normal")
                    btn_clean.configure(state="normal")
                    status_var.set("Eroare la procesare.")
                app.after(0, on_err)

        threading.Thread(target=task, daemon=True).start()

    def open_html_report() -> None:
        reps = state["reports"]  # type: ignore[assignment]
        if not reps:
            messagebox.showinfo("Info", "Rulează întâi o Scanare sau o Ștergere de metadate.")
            return
        html_str = render_html(reps)  # type: ignore[arg-type]
        out_file = Path(tempfile.gettempdir()) / "raport_hidden_scan.html"
        out_file.write_text(html_str, encoding="utf-8")
        webbrowser.open(out_file.as_uri())

    def open_output_folder() -> None:
        reps = state["reports"]  # type: ignore[assignment]
        if reps:
            first = reps[0]  # type: ignore[index]
            if first.clean_result and first.clean_result.output_file:
                _open_in_explorer(Path(first.clean_result.output_file))
                return
            _open_in_explorer(Path(first.file))
        elif state["targets"]:
            _open_in_explorer(Path(state["targets"][0]))

    btn_scan = ctk.CTkButton(
        act, text="1. Scanează Metadate & Date Ascunse", width=250, height=38,
        fg_color="#1f6aa5", hover_color="#144870",
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: run_worker(clean_mode=False),
    )
    btn_scan.pack(side="left", padx=(10, 8), pady=10)

    btn_clean = ctk.CTkButton(
        act, text="2. ȘTERGE METADATE (Curăță Fișiere / Director)", width=310, height=38,
        fg_color="#127848", hover_color="#0c5432",
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: run_worker(clean_mode=True),
    )
    btn_clean.pack(side="left", padx=8, pady=10)

    btn_html = ctk.CTkButton(
        act, text="Deschide Raport HTML", width=165, height=38,
        fg_color="#5a6268", hover_color="#3e444a",
        command=open_html_report,
    )
    btn_html.pack(side="left", padx=8, pady=10)

    btn_folder = ctk.CTkButton(
        act, text="Arată în Explorer", width=145, height=38,
        fg_color="#5a6268", hover_color="#3e444a",
        command=open_output_folder,
    )
    btn_folder.pack(side="left", padx=8, pady=10)

    status_bar = ctk.CTkLabel(app, textvariable=status_var, anchor="w", font=ctk.CTkFont(size=12))
    status_bar.pack(fill="x", padx=16, pady=(0, 10))

    # Dacă a fost lansat din Clic-Dreapta cu o acțiune automată ("scan" sau "clean")
    if state["targets"] and auto_action in ("scan", "clean"):
        app.after(200, lambda: run_worker(clean_mode=(auto_action == "clean")))

    app.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hidden-scan-gui")
    ap.add_argument("targets", nargs="*", help="fișiere sau directoare primite din clic-dreapta")
    ap.add_argument("--action", choices=["scan", "clean"], default="scan",
                    help="acțiunea executată automat la pornire")
    ap.add_argument("--in-place", action="store_true",
                    help="suprascrie fișierele originale la ștergerea metadatelor")
    args = ap.parse_args(argv)
    return run_gui(
        initial_targets=args.targets,
        auto_action=args.action if args.targets else None,
        in_place=args.in_place,
    )


if __name__ == "__main__":
    sys.exit(main())
