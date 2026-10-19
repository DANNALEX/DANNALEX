import {
  addDays,
  attendanceRate,
  buildInsights,
  countStatuses,
  dayStats,
  recordsFor,
  sortPeople,
  todayISO,
  workdaysEnding,
} from "../engine";
import { copy, formatPercent, formatLongDate, greeting, insightCopy, type Lang } from "../i18n";
import { useStore } from "../store";
import { Avatar } from "../ui";

export function Dashboard({ lang, onOpen }: { lang: Lang; onOpen: (view: "attendance" | "insights" | "team") => void }) {
  const { people, records } = useStore();
  const text = copy[lang];
  const today = todayISO();
  const stats = dayStats(people, records, today);
  const rate = attendanceRate(stats);
  const insights = buildInsights(people, records, today).slice(0, 3);
  const days = workdaysEnding(addDays(today, -1), 10);
  const known = recordsFor(people, records);
  const hour = new Date().getHours();

  return (
    <div className="stack">
      <header className="page-head">
        <p className="kicker">{formatLongDate(today, lang)}</p>
        <h1>{greeting(lang, hour)}</h1>
        <p className="lede">
          {text.peopleCount(people.length)} · {text.demo}
        </p>
      </header>

      <section className="kpis" aria-label={text.today}>
        <Kpi label={text.present} value={stats.present} tone="green" />
        <Kpi label={text.late} value={stats.late} tone="amber" />
        <Kpi label={text.absent} value={stats.absent} tone="red" />
        <Kpi label={text.pending} value={stats.pending} tone="ink" />
        <Kpi label={text.rate} value={formatPercent(rate, lang)} tone="green" />
      </section>

      <div className="split">
        <section className="card">
          <div className="card-head">
            <h2>{text.chartTitle}</h2>
            <p>{text.chartHint}</p>
          </div>
          <div className="chart" role="img" aria-label={text.chartTitle}>
            {days.map((day) => {
              const dayRate = attendanceRate(countStatuses(known.filter((record) => record.date === day)));
              const height = dayRate === null ? 0 : Math.round(dayRate * 100);
              return (
                <div key={day} className="bar" title={formatLongDate(day, lang)}>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ height: `${height}%` }} />
                  </div>
                  <span>{day.slice(8)}</span>
                </div>
              );
            })}
          </div>
        </section>

        <section className="card">
          <div className="card-head">
            <h2>{text.briefTitle}</h2>
            <button type="button" className="text-btn" onClick={() => onOpen("insights")}>
              {text.openInsights}
            </button>
          </div>
          {insights.length === 0 ? (
            <p className="muted">{text.briefEmpty}</p>
          ) : (
            <ul className="brief">
              {insights.map((insight) => {
                const item = insightCopy(lang, insight, people);
                return (
                  <li key={`${insight.kind}-${"personId" in insight ? insight.personId : insight.department}`}>
                    <strong>{item.title}</strong>
                    <span>{item.body}</span>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </div>

      <section className="card">
        <div className="card-head">
          <h2>{text.todayList}</h2>
          <button type="button" className="text-btn" onClick={() => onOpen("attendance")}>
            {text.navAttendance}
          </button>
        </div>
        {people.length === 0 ? (
          <button type="button" className="btn" onClick={() => onOpen("team")}>
            {text.addFromTeam}
          </button>
        ) : (
          <ul className="today-list">
            {sortPeople(people).map((person) => {
              const record = known.find((item) => item.personId === person.id && item.date === today);
              const status = record?.status ?? "pending";
              return (
                <li key={person.id}>
                  <Avatar name={person.name} id={person.id} />
                  <div>
                    <strong>{person.name}</strong>
                    <span>{person.department}</span>
                  </div>
                  <em className={`pill is-${status}`}>{text[status]}</em>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}

function Kpi({ label, value, tone }: { label: string; value: number | string; tone: string }) {
  return (
    <article className={`kpi tone-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
