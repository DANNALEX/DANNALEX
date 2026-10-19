import { useState, type FormEvent } from "react";
import {
  DEPARTMENTS,
  addDays,
  attendanceRate,
  countStatuses,
  createId,
  personError,
  recordsFor,
  sortPeople,
  todayISO,
  workdaysEnding,
  type Person,
} from "../engine";
import { copy, formatPercent, type Lang } from "../i18n";
import { useStore } from "../store";
import { Avatar } from "../ui";

const EMPTY = { name: "", role: "", department: "Inginerie", email: "" };

export function Team({ lang }: { lang: Lang }) {
  const store = useStore();
  const text = copy[lang];
  const [draft, setDraft] = useState(EMPTY);
  const [editing, setEditing] = useState<string | null>(null);
  const [error, setError] = useState<"name" | "email" | null>(null);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const past = new Set(workdaysEnding(addDays(todayISO(), -1), 10));
  const known = recordsFor(store.people, store.records).filter((record) => past.has(record.date));

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const problem = personError(draft);
    setError(problem);
    if (problem) return;
    const person: Person = {
      id: editing ?? createId(),
      name: draft.name.trim(),
      role: draft.role.trim(),
      department: draft.department.trim() || "Inginerie",
      email: draft.email.trim(),
    };
    store.savePerson(person);
    setDraft(EMPTY);
    setEditing(null);
    setError(null);
  }

  return (
    <div className="stack">
      <header className="page-head">
        <p className="kicker">{text.demo}</p>
        <h1>{text.navTeam}</h1>
        <p className="lede">{text.teamLead}</p>
      </header>

      <form className="card form" onSubmit={onSubmit}>
        <h2>{editing ? text.updatePerson : text.addPerson}</h2>
        <div className="form-grid">
          <label>
            {text.name}
            <input value={draft.name} maxLength={80} onChange={(event) => setDraft({ ...draft, name: event.target.value })} required />
          </label>
          <label>
            {text.role}
            <input value={draft.role} maxLength={80} onChange={(event) => setDraft({ ...draft, role: event.target.value })} />
          </label>
          <label>
            {text.department}
            <input
              list="departments"
              value={draft.department}
              maxLength={80}
              onChange={(event) => setDraft({ ...draft, department: event.target.value })}
            />
            <datalist id="departments">
              {DEPARTMENTS.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>
          </label>
          <label>
            {text.email}
            <input
              type="email"
              value={draft.email}
              maxLength={80}
              onChange={(event) => setDraft({ ...draft, email: event.target.value })}
            />
          </label>
        </div>
        {error ? (
          <p className="form-error" role="alert">
            {error === "name" ? text.nameError : text.emailError}
          </p>
        ) : null}
        <div className="row-actions">
          <button type="submit" className="btn">
            {editing ? text.updatePerson : text.savePerson}
          </button>
          {editing ? (
            <button
              type="button"
              className="btn ghost"
              onClick={() => {
                setEditing(null);
                setDraft(EMPTY);
                setError(null);
              }}
            >
              {text.cancel}
            </button>
          ) : null}
        </div>
      </form>

      {store.people.length === 0 ? (
        <p className="muted">{text.noPeople}</p>
      ) : (
        <ul className="team-grid">
          {sortPeople(store.people).map((person) => {
            const stats = countStatuses(known.filter((record) => record.personId === person.id));
            return (
              <li key={person.id} className="card team-card">
                <div className="person-id">
                  <Avatar name={person.name} id={person.id} />
                  <div>
                    <strong>{person.name}</strong>
                    <span>
                      {person.department}
                      {person.role ? ` · ${person.role}` : ""}
                    </span>
                  </div>
                </div>
                <p className="rate-line">
                  <span>{text.lastWindow}</span>
                  <strong>{formatPercent(attendanceRate(stats), lang)}</strong>
                </p>
                <p className="mini-counts">
                  {text.late} {stats.late} · {text.absent} {stats.absent} · {text.remote} {stats.remote}
                </p>
                {person.email ? <p className="email">{person.email}</p> : null}
                <div className="row-actions">
                  <button
                    type="button"
                    className="btn ghost"
                    onClick={() => {
                      setEditing(person.id);
                      setDraft({
                        name: person.name,
                        role: person.role,
                        department: person.department,
                        email: person.email,
                      });
                      setError(null);
                      setPendingDelete(null);
                    }}
                  >
                    {text.edit}
                  </button>
                  {pendingDelete === person.id ? (
                    <>
                      <button type="button" className="btn danger" onClick={() => store.deletePerson(person.id)}>
                        {text.confirmRemove}
                      </button>
                      <button type="button" className="btn ghost" onClick={() => setPendingDelete(null)}>
                        {text.cancel}
                      </button>
                    </>
                  ) : (
                    <button type="button" className="btn ghost" onClick={() => setPendingDelete(person.id)}>
                      {text.remove}
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
