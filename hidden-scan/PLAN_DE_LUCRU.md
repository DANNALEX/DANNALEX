# Plan de lucru — Aplicație Scanare și Ștergere Metadate (`hidden-scan` v3.0)

_Ultima actualizare: 2026-11-07_

## Obiectiv general

Aplicație locală pentru Windows (cu integrare în meniul **Clic-Dreapta din Windows Explorer** pe fișiere individuale și pe directoare, plus interfață grafică CustomTkinter și CLI) care **detectează** și **șterge complet metadatele și datele invizibile** din documente (`.pdf`, `.docx`, `.xlsx`), imagini (`.jpg`, `.jpeg`, `.png`, `.webp`) și fișiere text/cod (`.txt`, `.md`, `.csv`, `.json`, `.py`).

## Stare curentă

- **Implementare și testare finalizate (v3.0):** Toate cele 22 de teste unitare și end-to-end (`pytest`) trec fără nicio eroare sau avertisment (inclusiv testele de ștergere metadate pe PDF, DOCX, PNG, JPEG și directoare complete cu ignorarea fișierelor temporare Office `~$*`).

## Pași finalizați

- **2026-08-16** — Redactare raport de cercetare „Ce ascunde un fișier" și specificația CLI `hidden-scan-spec-v2.1.md` (trecută prin 2 runde de verificare pe hârtie). **De ce:** stabilirea bazei teoretice și a regulilor de detecție pentru metadate, OOXML, PDF, imagini și Unicode.
- **2026-11-07** — Verificare completă a planului și a specificației v2.1 (`RAPORT_VERIFICARE_PLAN_SI_SPECIFICATIE_V2.1.md`). **De ce:** identificarea diferențelor dintre specificația CLI (Linux) și cerința reală a utilizatorului pe Windows (ștergere metadate pe fișiere și directoare din clic-dreapta, fără dependență blocantă de `exiftool`).
- **2026-11-07** — Implementarea pachetului `hidden_scan` v3.0 (`model.py`, `config.py`, `utils.py`, `scanners/*`, `cleaner.py`, `core.py`, `report.py`, `cli.py`, `gui.py`). **De ce:** asigurarea detecției și ștergerii de metadate 100% nativ în Python (pentru PDF, Word/Excel, Imagini și Text), plus suport pentru directoare.
- **2026-11-07** — Crearea instalatorului Windows (`INSTALARE_APLICATIE.bat`, `install_context_menu.ps1`, `uninstall_context_menu.ps1`, `launcher.ps1`, `PORNESTE_APLICATIA.bat`). **De ce:** instalare cu 1 clic a meniului Clic-Dreapta în Windows Explorer pe fișiere și pe directoare.
- **2026-11-07** — Rularea și validarea celor 22 de teste automate și încrucișate (`pytest -v` → 22 passed). **De ce:** confirmarea că după curățare, re-scanarea fișierelor (PDF, DOCX, PNG, JPG) și a directoarelor raportează `0` metadate sensibile și risc `LOW`.

## Pași următori

- Rularea `INSTALARE_APLICATIE.bat` pe PC-ul Windows pentru activarea cheilor de registru `HKCU` (Clic-Dreapta) și a scurtăturii de pe Desktop.

## Decizii care așteaptă clarificare

- Niciuna.

## Riscuri și blocaje cunoscute

- **Lipsa `exiftool.exe` pe Windows:** Rezolvat prin implementarea citirii și ștergerii de metadate 100% nativ în Python (`pikepdf`, `Pillow`, `zipfile`/`xml.etree`), păstrând `exiftool` doar ca supliment opțional.
- **Fișiere Office deschise (`~$*.docx` / `~$*.xlsx`):** Rezolvat prin filtrarea automată a fișierelor temporare `~$` la parcurgerea directoarelor.
