import { useMemo, useState } from "react";
import { addDays, attendanceRate, countStatuses, reportRows, recordsFor, todayISO, toCsv, workdaysEnding } from "../engine";
import { copy, formatPercent, type Lang } from "../i18n";
import { useStore } from "../store";

export function Reports({ lang }: { lang: Lang }) {
  const { people, records } = useStore();
  const text = copy[lang];
  const today = todayISO();
  const past = workdaysEnding(addDays(today, -1), 10);
  const [from, setFrom] = useState(past[0] ?? today);
  const [to, setTo] = useState(today);
  const start = from <= to ? from : to;
  const end = from <= to ? to : from;
  const rows = useMemo(() => reportRows(people, records, start, end), [people, records, start, end]);
  const known = recordsFor(people, records).filter((record) => record.date >= start && record.date <= end);
  const rate = attendanceRate(countStatuses(known));

  function download() {
    const csv = `\uFEFF${toCsv(people, records, start, end)}`;
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `prezenta-v9-${start}-${end}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="stack">
      <header className="page-head">
        <p className="kicker">{text.rows}: {known.length}</p>
        <h1>{text.navReports}</h1>
        <p className="lede">{text.reportsLead}</p>
      </header>

      <div className="toolbar">
        <label className="field">
          {text.from}
          <input type="date" value={from} max={today} onChange={(event) => event.target.value && setFrom(event.target.value)} />
        </label>
        <label className="field">
          {text.to}
          <input type="date" value={to} max={today} onChange={(event) => event.target.value && setTo(event.target.value)} />
        </label>
        <button type="button" className="btn" onClick={download} disabled={known.length === 0}>
          {text.export}
        </button>
      </div>

      <section className="kpis slim">
        <article className="kpi">
          <span>{text.rate}</span>
          <strong>{formatPercent(rate, lang)}</strong>
        </article>
        <article className="kpi">
          <span>{text.rows}</span>
          <strong>{known.length}</strong>
        </article>
        <article className="kpi">
          <span>{text.absent}</span>
          <strong>{countStatuses(known).absent}</strong>
        </article>
      </section>

      {rows.length === 0 ? (
        <p className="muted">{text.emptyRange}</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{text.person}</th>
                <th>{text.department}</th>
                <th>{text.present}</th>
                <th>{text.late}</th>
                <th>{text.absent}</th>
                <th>{text.remote}</th>
                <th>{text.leave}</th>
                <th>{text.rate}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.person.id}>
                  <td>{row.person.name}</td>
                  <td>{row.person.department}</td>
                  <td>{row.stats.present}</td>
                  <td>{row.stats.late}</td>
                  <td>{row.stats.absent}</td>
                  <td>{row.stats.remote}</td>
                  <td>{row.stats.leave}</td>
                  <td>{formatPercent(row.rate, lang)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
