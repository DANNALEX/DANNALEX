import { useEffect, useState } from "react";
import { DEMO_ORG } from "./engine";
import { copy, type Lang } from "./i18n";
import { useStore } from "./store";
import { Attendance } from "./views/Attendance";
import { Dashboard } from "./views/Dashboard";
import { Insights } from "./views/Insights";
import { Reports } from "./views/Reports";
import { Team } from "./views/Team";

const VIEWS = ["dashboard", "attendance", "team", "insights", "reports"] as const;
type View = (typeof VIEWS)[number];

function readView(): View {
  const hash = window.location.hash.replace("#", "");
  return VIEWS.includes(hash as View) ? (hash as View) : "dashboard";
}

export function App() {
  const store = useStore();
  const lang = store.lang;
  const text = copy[lang];
  const [view, setView] = useState<View>(readView);

  useEffect(() => {
    const onPop = () => setView(readView());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  function open(next: View) {
    const url = `${window.location.pathname}${window.location.search}#${next}`;
    window.history.pushState(null, "", url);
    setView(next);
  }

  const titles: Record<View, string> = {
    dashboard: text.navDashboard,
    attendance: text.navAttendance,
    team: text.navTeam,
    insights: text.navInsights,
    reports: text.navReports,
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="mark" aria-hidden="true">
            V9
          </span>
          <div className="brand-copy">
            <strong>{text.product}</strong>
            <p>{DEMO_ORG}</p>
          </div>
        </div>
        <nav className="nav" aria-label={text.product}>
          {VIEWS.map((item) => (
            <button key={item} type="button" aria-current={view === item ? "page" : undefined} onClick={() => open(item)}>
              {titles[item]}
            </button>
          ))}
        </nav>
        <div className="side-foot">
          <div className="lang" role="group" aria-label={text.language}>
            {(["ro", "en"] as Lang[]).map((item) => (
              <button key={item} type="button" aria-pressed={lang === item} onClick={() => store.setLang(item)}>
                {item.toUpperCase()}
              </button>
            ))}
          </div>
          <p>{text.stored}</p>
          <button type="button" className="btn ghost block" onClick={() => store.reset()}>
            {text.reset}
          </button>
        </div>
      </aside>
      <main className="main" data-view={view}>
        <div className="wrap">
          {view === "dashboard" ? <Dashboard lang={lang} onOpen={open} /> : null}
          {view === "attendance" ? <Attendance lang={lang} /> : null}
          {view === "team" ? <Team lang={lang} /> : null}
          {view === "insights" ? <Insights lang={lang} /> : null}
          {view === "reports" ? <Reports lang={lang} /> : null}
        </div>
      </main>
    </div>
  );
}
