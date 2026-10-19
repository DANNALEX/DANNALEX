import { useState } from "react";
import { answerQuestion, buildInsights, todayISO } from "../engine";
import { answerCopy, copy, insightCopy, type Lang } from "../i18n";
import { useStore } from "../store";

export function Insights({ lang }: { lang: Lang }) {
  const { people, records } = useStore();
  const text = copy[lang];
  const insights = buildInsights(people, records, todayISO());
  const [question, setQuestion] = useState("");
  const [asked, setAsked] = useState<string | null>(null);

  function ask(value: string) {
    const next = value.trim();
    setQuestion(value);
    setAsked(next);
  }

  const answer = asked === null ? null : answerQuestion(asked, people, records, todayISO());

  return (
    <div className="stack">
      <header className="page-head">
        <p className="kicker">{text.askHint}</p>
        <h1>{text.navInsights}</h1>
        <p className="lede">{text.insightsLead}</p>
      </header>

      <section className="card ask">
        <h2>{text.askTitle}</h2>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            ask(question);
          }}
        >
          <input
            value={question}
            placeholder={text.askPlaceholder}
            onChange={(event) => setQuestion(event.target.value)}
            aria-label={text.askTitle}
          />
          <button type="submit" className="btn">
            {text.ask}
          </button>
        </form>
        <div className="chips">
          {text.suggestions.map((suggestion) => (
            <button key={suggestion} type="button" className="chip" onClick={() => ask(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
        {answer ? (
          <p className="answer" role="status">
            {answerCopy(lang, answer, people)}
          </p>
        ) : null}
      </section>

      {insights.length === 0 ? (
        <p className="muted">{text.noInsights}</p>
      ) : (
        <ul className="insight-list">
          {insights.map((insight) => {
            const item = insightCopy(lang, insight, people);
            return (
              <li key={`${insight.kind}-${"personId" in insight ? insight.personId : insight.department}`} className={`card insight is-${insight.kind}`}>
                <p className="kicker">{item.title}</p>
                <p>{item.body}</p>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
