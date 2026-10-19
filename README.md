# AI Attendance Manager V9

Registru de prezență pentru o echipă mică. Datele demonstrative sunt pentru **Atelier Nord** și rămân în browser (`localStorage`), fără server.

## Ce face

- Panou cu situația de azi, rata ultimelor 10 zile lucrătoare și un rezumat al semnalelor.
- Prezență pe zi: prezent, întârziat, absent, remote sau concediu. Schimbările se salvează imediat.
- Echipă: adăugare, editare, ștergere.
- Analiză pe reguli (întârzieri repetate, absențe apropiate, acoperire, remote, serie) și întrebări peste registru.
- Rapoarte pe interval și export CSV.

Interfața este în română și engleză.

## Pornire

```bash
npm install
npm test
npm run dev
```

Aplicația se deschide la `http://127.0.0.1:5173`.

```bash
npm run build
npm run preview
```
