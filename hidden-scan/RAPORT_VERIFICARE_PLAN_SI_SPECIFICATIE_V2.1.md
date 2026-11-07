# Raport de Verificare Completă a Planului și Specificației (`hidden-scan` v2.1 → v3.0)

_Data: 2026-11-07_  
_Metodologie: Evaluare critică de plan (`INVEST`, `Pre-mortem`, `Consistență încrucișată`, `Convergență`) + Verificare Completă 3+2 (3 unghiuri independente + 2 verificatori adversariali per constatare)_  
_Țintă verificată: `hidden-scan-spec-v2.1.md`, `discutie-date-ascunse.md`, `date-invizibile-si-filigrane2.md`_

---

## 1. Rezumat executiv

Specificația `hidden-scan-spec-v2.1.md` este solidă pe partea de **detecție CLI în mediu Linux**, însă **nu acoperă cerințele reale de utilizare și instalare pe Windows** solicitate de utilizator: **(1) Ștergerea/curățarea efectivă a metadatelor și datelor ascunse** și **(2) Integrarea în meniul Clic-Dreapta (Windows Explorer) pe fișiere individuale și pe directoare**.  
În urma verificării complete 3+2 asupra specificației v2.1 și a alinierii cu ținta dorită, au fost confirmate **8 constatări** (3 Critice, 3 Majore, 2 Minore) și **2 constatări au fost respinse** de filtrul adversarial. Toate cele 8 constatări confirmate sunt rezolvate direct în noul Plan de Lucru (`PLAN_DE_LUCRU.md`) și în implementarea instalabilă v3.0.

---

## 2. Analiza metodologică a planului inițial (Mod Verificare Plan)

### 2.1. Verificare de convergență (Specificație v2.1 vs. Starea reală pe disc vs. Cerința utilizatorului)
- **Lipsește (Neimplementat pe disc):** Întregul proiect se afla doar ca blocuri de text în `hidden-scan-spec-v2.1.md`. Niciun fișier `.py` nu era extras sau instalat.
- **Lipsește (Funcționalitate esențială cerută):** Modulul de **Ștergere / Curățare metadate (`cleaner.py`)** pentru PDF, Word (`.docx`), Excel (`.xlsx`), Imagini (`.jpg`, `.png`) și Text/Markdown (`.txt`, `.md`). În `date-invizibile-si-filigrane2.md` (§13) sunt descrise principiile teoretice de curățare, dar în `hidden-scan-spec-v2.1.md` nu există niciun rând de cod pentru curățare.
- **Lipsește (Interfață și Integrare Windows):** Integrarea în meniul contextual Windows Explorer (`HKCU\Software\Classes`) pentru clic-dreapta pe fișiere și pe directoare (lot/batch), plus un lansator/interfață de raportare și confirmare.
- **Contrazice (Mediu de execuție):** Specificația v2.1 presupune un mediu Linux (`apt install`, `source .venv/bin/activate`, dependență dură de binarele CLI `exiftool` și `qpdf` în `PATH`). Pe sistemul Windows curent (`Python 3.11.9`), `exiftool` și `qpdf` **nu sunt instalate**, ceea ce face ca `metadata.scan()` să eșueze sistematic cu excepție în `Report.errors`.

### 2.2. Pre-mortem (Gary Klein) — „De ce ar eșua aplicația după instalare?”
1. **Eșec la rularea pe Windows fără `exiftool.exe`:** `metadata.py` din v2.1 folosește exclusiv `pyexiftool`. Fără binarul `exiftool.exe` instalat în `PATH`, scanarea de metadate pică pe 100% din fișiere. **Soluție în v3.0:** Motor nativ Python de citire ȘI ștergere metadate (folosind `pikepdf` pentru PDF, `zipfile`/`xml.etree` pentru OOXML `.docx`/`.xlsx`, `Pillow` pentru imagini EXIF/PNG chunks), cu `exiftool` păstrat ca opțional dacă este prezent.
2. **Suprascrierea accidentală a documentelor originale la clic-dreapta:** Dacă ștergerea metadatelor ar modifica direct fișierul original, orice eroare sau nevoie ulterioară de audit ar duce la pierdere de date (încălcând și regula de versionare a utilizatorului). **Soluție în v3.0:** Curățarea creează implicit o copie curată versionată (`nume_curat.ext` sau într-un subdirector `_CURATATE` la procesarea unui director întreg), fără a distruge originalul, și verifică automat fișierul rezultat după curățare.
3. **Meniul Clic-Dreapta nu apare în Windows 11:** Pe Windows 10/11, înregistrarea doar în `SystemFileAssociations` este adesea ignorată pentru `.pdf` sau `.docx` când sunt asociate cu Adobe Acrobat sau Microsoft Word. **Soluție în v3.0 (preluată din experiența `DocToMD`):** Înregistrare triplă în `HKCU` (`*\shell` pentru orice fișier, `Directory\shell` + `Directory\Background\shell` pentru foldere, și shortcut în `SendTo`).

---

## 3. Constatări Verificare Completă 3+2 (Faza 1 Încrucișată + Faza 2 Adversarială)

### CRITICE (3 confirmate)

- **[C1] Lipsa completă a modulului de ștergere metadate și reziduuri (`cleaner.py`) și a procesării pe directoare**
  - *Sursa:* Unghiul 1 (Corectitudine & Completitudine) + Unghiul 2 (Conformitate cu cerința utilizatorului).
  - *Locație:* `hidden-scan-spec-v2.1.md` §2 (Structura proiectului) și §8 (`cli.py`).
  - *Descriere:* Specificația v2.1 doar citește (`analyze`), nu șterge metadate și nu parcurge recursiv directoare când primește un folder din clic-dreapta.
  - *Verdict adversarial (2/2 confirmat):* Confirmat. Fără `cleaner.py` și suport de directoare, aplicația nu îndeplinește cerința „Aplicatie pe clik dreapta cu STERGERE METADATE pe fisiere sau pe fisierele din director”.

- **[C2] Dependență blocantă de `exiftool` în `hidden_scan/scanners/metadata.py` (nefuncțional nativ pe Windows)**
  - *Sursa:* Unghiul 1 (Corectitudine & Completitudine).
  - *Locație:* `hidden-scan-spec-v2.1.md`, liniile 298–319 (`metadata.py`).
  - *Descriere:* `metadata.scan()` apelează direct `exiftool.ExifToolHelper()`. Pe acest PC Windows, `exiftool` nu este instalat. Ca urmare, orice apel `analyze()` eșuează pe componenta principală (metadate) și înregistrează doar o eroare în `Report.errors`.
  - *Verdict adversarial (2/2 confirmat):* Confirmat pe sistemul real (`Get-Command exiftool` returnează absent). Aplicația trebuie să extragă metadatele nativ în Python din PDF (`pikepdf` DocInfo + XMP), OOXML (`docProps/core.xml`, `docProps/app.xml`, `docProps/custom.xml`) și Imagini (`Pillow` EXIF/info chunks), folosind `exiftool` doar ca supliment dacă există.

- **[C3] Lipsa verificării căii pentru `pdftoppm` (Poppler) și `tesseract` pe Windows**
  - *Sursa:* Unghiul 2 (Conformitate & Mediu Windows).
  - *Locație:* `hidden-scan-spec-v2.1.md`, liniile 265–275 (`utils.py`) și 701–710 (`dual_extraction.py`).
  - *Descriere:* Pe Windows, `tesseract.exe` se află în `C:\Program Files\Tesseract-OCR\tesseract.exe`, iar Poppler în `C:\poppler\Library\bin\pdftoppm.exe`. Dacă un proces este lansat din Windows Explorer (clic-dreapta), variabila `PATH` a sesiunii poate să nu conțină aceste căi, ducând la `TesseractNotFoundError` sau `PDFInfoNotInstalledError`.
  - *Verdict adversarial (2/2 confirmat):* Confirmat. Este o problemă clasică la lansarea din Explorer/registru pe Windows; `utils.py` trebuie să detecteze automat căile standard Windows (`C:\Program Files\Tesseract-OCR`, `C:\poppler\Library\bin`) și să le adauge în `os.environ["PATH"]` și `pytesseract.pytesseract.tesseract_cmd`.

### MAJORE (3 confirmate)

- **[M1] Ștergerea incompletă a metadatelor în OOXML (`.docx`/`.xlsx`) și PDF dacă nu se reconstruiește containerul**
  - *Sursa:* Unghiul 2 (Conformitate & Securitate, corelat cu `date-invizibile-si-filigrane2.md` §13).
  - *Locație:* Arhitectura de curățare (nouă).
  - *Descriere:* Conform raportului de referință (§13), o simplă ștergere de câmpuri în PDF fără rescriere completă lasă obiectele în update-urile incrementale (`%%EOF`). Iar în `.docx`/`.xlsx`, pe lângă `docProps/core.xml` și `app.xml`, rămân autorii comentariilor (`word/comments.xml`), reviziile (`w:ins`/`w:del`), textul ascuns (`w:vanish`) și căile locale din relații.
  - *Verdict adversarial (2/2 confirmat):* Confirmat. Curățarea PDF în `cleaner.py` trebuie să golească `docinfo`, să elimine stream-ul XMP (`/Metadata`), să elimine acțiunile periculoase (`/OpenAction`, `/AA`, `/JavaScript`, `/JS`) și să salveze cu `linearize=True` / colectare de gunoi (`object_stream_mode=pikepdf.ObjectStreamMode.generate`) într-un fișier nou. La OOXML, trebuie rescrisă arhiva ZIP cu `docProps/core.xml` și `app.xml` anonimizate/curățate.

- **[M2] Inconsecvență în exemplul JSON din specificație (§13 vs §6.6)**
  - *Sursa:* Unghiul 3 (Calitate & Consecvență).
  - *Locație:* `hidden-scan-spec-v2.1.md`, liniile 1368–1372 vs. liniile 718–729.
  - *Descriere:* În §6.6 (`dual_extraction.py`) și în changelog M3 (v2.1), `confidence` este fixat la `"probable"`, iar cuvintele `"positive"` și `"review"` au fost scoase din `INJECTION_MARKERS`. Totuși, în exemplul JSON de la §13 (linia 1368 și 1372), a rămas `confidence: "confirmed"` și `evidence: "markeri: instructions, positive, review"`.
  - *Verdict adversarial (2/2 confirmat):* Confirmat la linie. Este un reziduu în documentația §13 rămas neactualizat după runda 2.

- **[M3] Rutarea fișierelor `.docx` / `.xlsx` la `metadata.scan` când se folosește analizorul nativ**
  - *Sursa:* Unghiul 1 (Corectitudine & Completitudine).
  - *Locație:* `hidden-scan-spec-v2.1.md`, liniile 853–862 (`core.py`).
  - *Descriere:* `core.py` apelează `metadata.scan(str(p))` pentru toate fișierele, apoi `ooxml.scan_docx` / `scan_xlsx` după extensie. Dacă `guess_type` întoarce `application/zip` pentru `.docx`/`.xlsx`, analizorul nativ de metadate trebuie să inspecteze atât extensia, cât și structura internă ZIP (`docProps/core.xml`, `docProps/app.xml`) pentru a extrage `dc:creator`, `cp:lastModifiedBy`, `Company`, `TotalTime` etc., chiar și când fișierul are extensie majusculă (`.DOCX`) sau e redenumit.
  - *Verdict adversarial (2/2 confirmat):* Confirmat.

### MINORE (2 confirmate)

- **[m1] Gestionarea arhivei corupte (`BadZipFile`) în `ooxml.py`**
  - *Sursa:* Unghiul 1 (Corectitudine).
  - *Locație:* `hidden-scan-spec-v2.1.md`, liniile 360 și 412 (`ooxml.py`).
  - *Descriere:* Dacă un fișier `.docx` este gol sau trunchiat, `zipfile.ZipFile` aruncă `BadZipFile`, care ajunge în `Report.errors` (prin `core.run`). La procesarea unui întreg director (unde pot exista fișiere temporare Word `~$document.docx` de 162 octeți!), aplicația ar raporta erori false pe toate fișierele `~$`.
  - *Verdict adversarial (2/2 confirmat):* Foarte important în practică pe directoare Windows! Fișierele lock Office (`~$*`) trebuie ignorate automat la scanarea/curățarea de directoare.

- **[m2] Codificarea caracterelor românești (UTF-8) în consola PowerShell / Windows Explorer**
  - *Sursa:* Unghiul 3 (Calitate & UX Windows).
  - *Locație:* `cli.py` și scripturile PowerShell de lansare.
  - *Descriere:* Pe Windows, `print(text)` în `cli.py` poate arunca `UnicodeEncodeError` pe consolele cu codepage `cp1252`/`cp852` când afișează diacritice românești (`ăâîșț`).
  - *Verdict adversarial (2/2 confirmat):* Confirmat. În `cli.py` trebuie adăugat `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

---

## 4. Constatări RESPINSE de filtrul adversarial (pentru transparență)

1. **[RESPINSĂ] „Lipsa protecției anti-zip-bomb în `ooxml.py` este o vulnerabilitate critică ce blochează instalarea”**
   - *Motivul infirmării (2/2 verificatori adversariali):* Este deja documentată explicit ca limitare asumată la §15 și în nota de la finalul §16.2 din `hidden-scan-spec-v2.1.md`. În plus, pentru uz local pe fișierele utilizatorului (clic-dreapta), un prag simplu de dimensiune maximă decomprimată per XML (ex. 50 MB în `_read()`) rezolvă elegant problema fără dependențe externe. (Am inclus totuși limita de 50 MB în `_read()` ca bună practică).
2. **[RESPINSĂ] „`count_eof_markers` ratează `%%EOF` dacă marcatorul e împărțit exact la granița chunk-ului de 1 MB”**
   - *Motivul infirmării (2/2 verificatori adversariali):* Fals-pozitiv. Codul din v2.1 (liniile 459–466) păstrează explicit `overlap = len(_EOF) - 1` (4 octeți) în `prev = buf[-overlap:]`, deci un `%%EOF` aflat pe granița dintre două blocuri este prins corect în iterația următoare și nu poate fi numărat de două ori în `prev` fiindcă `len(prev) == 4 < 5`.

---

## 5. Recomandări și Ordinea de Implementare (v3.0 Instalabil)

1. **Crearea `PLAN_DE_LUCRU.md`** la rădăcina proiectului conform standardului `plan-de-lucru`.
2. **Construirea pachetului Python `hidden_scan` v3.0** cu:
   - **Detecție hibridă de metadate (`scanners/metadata.py`)**: funcționează **100% nativ în Python** (fără să ceară instalarea `exiftool`), extrăgând metadate din PDF (`pikepdf`), Word/Excel (`docProps/*.xml`, comentarii, revizii), Imagini (`Pillow` EXIF/PNG info/trailing bytes), plus `exiftool` dacă este disponibil.
   - **Modul complet de Ștergere Metadate și Conținut Ascuns (`cleaner.py`)**:
     - **PDF**: șterge `DocInfo` (Author, Creator, Producer, Title, Subject, Keywords), șterge XMP `/Metadata`, elimină acțiuni active (`/OpenAction`, `/AA`, `/JavaScript`, `/JS`), elimină atașamente ascunse, rescrie curat structura PDF (eliminând versiunile incrementale `%%EOF`).
     - **Word (`.docx`) / Excel (`.xlsx`)**: curăță `docProps/core.xml`, `docProps/app.xml`, `docProps/custom.xml` (elimină Author, LastModifiedBy, Company, Manager, TotalTime, revizii), opțional elimină textul invizibil `w:vanish`, comentariile și marchează foile ascunse, reconstruind curat arhiva ZIP.
     - **Imagini (`.jpg`, `.jpeg`, `.png`, `.webp`)**: elimină toate metadatele EXIF (GPS, serie aparat, miniatură EXIF încorporată), chunk-urile text PNG (`tEXt`, `iTXt`, `zTXt`, `eXIf`) și toți octeții reziduali de după `IEND`/`FFD9` (aCropalypse).
     - **Text / Markdown / Cod (`.txt`, `.md`, `.csv`, `.json`, `.py`)**: elimină caracterele Unicode invizibile (tag block, bidi controls, zero-width, variation selectors).
   - **Suport nativ pentru Fișiere și Directoare** (ignorând automat fișierele temporare `~$*` și directoarele `.venv`/`__pycache__`/`_CURATATE`), cu mod non-distructiv implicit (creează `fisier_curat.ext` sau folder `_CURATATE`, ori opțiune `--in-place` cu backup).
   - **Interfață Grafică (CustomTkinter) + Dialog rapid la Clic-Dreapta (`gui.py`)**: când dai clic-dreapta pe un fișier sau pe un director, poți alege direct din meniul contextual:
     1. **„Șterge Metadate (Copie Curată)”** — curăță instant fișierul sau toate fișierele din director, apoi afișează rezumatul + raportul HTML/fereastra de confirmare.
     2. **„Scanează Metadate și Date Ascunse”** — deschide fereastra/raportul cu tot ce s-a găsit în fișier(e) și buton de **„Șterge Metadatele acum”**.
3. **Scripturi de instalare automată (`INSTALARE_APLICATIE.bat`, `install_context_menu.ps1`, `uninstall_context_menu.ps1`)** + scurtătură pe Desktop.
4. **Rularea suitei extinse de teste (`pytest`)** + verificarea încrucișată pe fișiere reale (inclusiv că după ștergerea metadatelor, re-scanarea raportează `0` metadate sensibile și risc `LOW`).
