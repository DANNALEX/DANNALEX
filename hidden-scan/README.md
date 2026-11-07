# hidden-scan v3.0 — Aplicație Scanare și Ștergere Metadate & Conținut Ascuns

Aplicație completă pentru Windows (cu **Meniu Clic-Dreapta în Windows Explorer** pe fișiere și pe directoare, **Interfață Grafică CustomTkinter** și **CLI**) care detectează și șterge metadatele și conținutul invizibil din:
- **PDF (`.pdf`)**: `DocInfo` (Author, Creator, Producer, Title, Subject, Keywords), stream-ul XMP (`/Metadata`), elemente active (`/OpenAction`, `/JavaScript`, `/JS`, `/AA`), atașamente ascunse și istoric incremental (`%%EOF`).
- **Word / Excel / PowerPoint (`.docx`, `.xlsx`, `.pptx`)**: `docProps/core.xml` (Autor, LastModifiedBy, Revizii), `docProps/app.xml` (Companie, Manager, Timp editare), `docProps/custom.xml`, autori comentarii, text marcat Hidden (`w:vanish`), foi ascunse (`hidden` / `veryHidden`).
- **Imagini (`.jpg`, `.jpeg`, `.png`, `.webp`)**: EXIF complet (GPS, serie aparat, proprietar, software), miniatură EXIF încorporată, chunk-uri text PNG și octeți reziduali după `IEND` / `FFD9` (aCropalypse).
- **Text / Cod (`.txt`, `.md`, `.csv`, `.json`, `.py`)**: caractere Unicode invizibile (ASCII smuggling tag block, controale bidi, zero-width, variation selectors).

---

## Instalare rapidă pe Windows (1 clic)

Rulează cu dublu-clic fișierul:
```text
INSTALARE_APLICATIE.bat
```

Acesta face automat toți pașii:
1. Instalează pachetul `hidden-scan` și bibliotecile necesare (`pikepdf`, `pdfminer.six`, `Pillow`, `jinja2`, `customtkinter`, `python-docx`, `reportlab`, `pytest`).
2. Rulează testele de verificare (`pytest`).
3. Înregistrează opțiunile în **Meniul Clic-Dreapta din Windows Explorer** (fără a necesita drepturi de Administrator — scrie în `HKCU\Software\Classes`):
   - **Pe orice fișier**:
     - `Șterge Metadate (Copie Curată)` — creează `nume_curat.ext` fără metadate și afișează raportul de verificare înainte/după.
     - `Scanează Metadate și Date Ascunse` — deschide fereastra cu toate metadatele și datele invizibile găsite.
   - **Pe orice director (sau pe fundalul unui director deschis)**:
     - `Șterge Metadate (Toate fișierele din director)` — parcurge toate fișierele din director (ignorând automat fișierele temporare Office `~$*`) și salvează versiunile curate în subdirectorul `_CURATATE\`.
     - `Scanează Metadate (Tot directorul)` — scanează toate fișierele din director și afișează raportul centralizat.
4. Creează scurtătura **„Scanare & Ștergere Metadate”** pe Desktop și în meniul **Send To**.

---

## Utilizare din Linie de Comandă (CLI)

```powershell
# 1. Scanare fișier sau director
hidden-scan document.pdf
hidden-scan "C:\Cale\Catredosar" --html raport.html --open-html

# 2. Ștergere metadate pe un fișier (creează document_curat.pdf)
hidden-scan document.pdf --clean

# 3. Ștergere metadate pe toate fișierele dintr-un director (salvează în _CURATATE\)
hidden-scan "C:\Cale\Catredosar" --clean --html raport_curatare.html

# 4. Ștergere metadate direct pe fișierele originale (in-place)
hidden-scan document.pdf --clean --in-place
```
