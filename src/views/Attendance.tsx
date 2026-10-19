import { useMemo, useState } from "react";
import {
  addDays,
  dayStats,
  defaultTimes,
  departmentsOf,
  sortPeople,
  todayISO,
  type Status,
} from "../engine";
import { copy, formatLongDate, type Lang } from "../i18n";
import { useStore } from "../store";
import { Avatar } from "../ui";

const STATUSES: Status[] = ["present", "late", "absent", "remote", "leave"];

export function Attendance({ lang }: { lang: Lang }) {
  const store = useStore();
  const text = copy[lang];
  const today = todayISO();
  const [date, setDate] = useState(today);
  const [department, setDepartment] = useState("all");
  const [onlyPending, setOnlyPending] = useState(false);
  const departments = departmentsOf(store.people);
  const stats = dayStats(store.people, store.records, date);

  const rows = useMemo(() => {
    return sortPeople(store.people).filter((person) => {
      if (department !== "all" && person.department !== department) return false;
      const record = store.records.find((item) => item.personId === person.id && item.date === date);
      if (onlyPending && record) return false;
      return true;
    });
  }, [store.people, store.records, department, onlyPending, date]);

  function setStatus(personId: string, status: Status) {
    const current = store.records.find((item) => item.personId === personId && item.date === date);
    const times = status === "absent" || status === "leave" ? {} : defaultTimes(status);
    store.upsert({
      personId,
      date,
      status,
      note: current?.note,
      ...times,
    });
  }

  return (
    <div className="stack">
      <header className="page-head">
        <p className="kicker">{text.saved}</p>
        <h1>{text.navAttendance}</h1>
        <p className="lede">{text.attendanceLead}</p>
      </header>

      <div className="toolbar">
        <div className="date-nav">
          <button type="button" className="btn ghost" onClick={() => setDate(addDays(date, -1))} aria-label={text.previous}>
            ←
          </button>
          <label className="date-field">
            <span className="sr">{formatLongDate(date, lang)}</span>
            <input
              type="date"
              value={date}
              max={today}
              onChange={(event) => {
                const next = event.target.value;
                if (next && next <= today) setDate(next);
              }}
            />
          </label>
          <button
            type="button"
            className="btn ghost"
            onClick={() => setDate(addDays(date, 1))}
            disabled={date >= today}
            aria-label={text.next}
          >
            →
          </button>
        </div>
        <label className="field inline">
          <span className="sr">{text.department}</span>
          <select value={department} onChange={(event) => setDepartment(event.target.value)}>
            <option value="all">{text.allDepartments}</option>
            {departments.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="check">
          <input type="checkbox" checked={onlyPending} onChange={(event) => setOnlyPending(event.target.checked)} />
          {text.onlyPending}
        </label>
        <button type="button" className="btn" onClick={() => store.markUnmarkedPresent(date)} disabled={stats.pending === 0}>
          {text.markRest}
        </button>
      </div>

      <p className="chips">
        <span>{formatLongDate(date, lang)}</span>
        <span>
          {text.present} {stats.present}
        </span>
        <span>
          {text.late} {stats.late}
        </span>
        <span>
          {text.absent} {stats.absent}
        </span>
        <span>
          {text.pending} {stats.pending}
        </span>
      </p>

      {rows.length === 0 ? (
        <p className="muted">{text.emptyFilter}</p>
      ) : (
        <ul className="people">
          {rows.map((person) => {
            const record = store.records.find((item) => item.personId === person.id && item.date === date);
            const timed = record && record.status !== "absent" && record.status !== "leave";
            return (
              <li key={person.id} className="person-card">
                <div className="person-id">
                  <Avatar name={person.name} id={person.id} />
                  <div>
                    <strong>{person.name}</strong>
                    <span>
                      {person.department} · {person.role}
                    </span>
                  </div>
                </div>
                <div className="status-row" role="group" aria-label={person.name}>
                  {STATUSES.map((status) => (
                    <button
                      key={status}
                      type="button"
                      className={`seg is-${status}${record?.status === status ? " on" : ""}`}
                      aria-pressed={record?.status === status}
                      onClick={() => setStatus(person.id, status)}
                    >
                      {text[status]}
                    </button>
                  ))}
                  {record ? (
                    <button type="button" className="seg ghost" onClick={() => store.clearMark(person.id, date)}>
                      {text.clear}
                    </button>
                  ) : null}
                </div>
                {timed ? (
                  <div className="times">
                    <label>
                      {text.checkIn}
                      <input
                        type="time"
                        value={record.checkIn ?? ""}
                        onChange={(event) => store.upsert({ ...record, checkIn: event.target.value || undefined })}
                      />
                    </label>
                    <label>
                      {text.checkOut}
                      <input
                        type="time"
                        value={record.checkOut ?? ""}
                        onChange={(event) => store.upsert({ ...record, checkOut: event.target.value || undefined })}
                      />
                    </label>
                    <label className="grow">
                      {text.note}
                      <input
                        type="text"
                        maxLength={140}
                        placeholder={text.notePlaceholder}
                        value={record.note ?? ""}
                        onChange={(event) => store.upsert({ ...record, note: event.target.value || undefined })}
                      />
                    </label>
                  </div>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
