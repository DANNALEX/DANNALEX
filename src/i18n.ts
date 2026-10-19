import type { Answer, Insight, Person, Status } from "./engine";

export type Lang = "ro" | "en";

export const copy = {
  ro: {
    product: "AI Attendance Manager",
    version: "V9",
    orgHint: "Registru local",
    navDashboard: "Panou",
    navAttendance: "Prezență",
    navTeam: "Echipă",
    navInsights: "Analiză",
    navReports: "Rapoarte",
    language: "Limbă",
    stored: "Datele rămân în acest browser.",
    reset: "Reîncarcă demo",
    greetingMorning: "Bună dimineața",
    greetingAfternoon: "Bună ziua",
    greetingEvening: "Bună seara",
    peopleCount: (n: number) => `${n} oameni`,
    present: "Prezenți",
    late: "Întârziați",
    absent: "Absenți",
    remote: "Remote",
    leave: "Concediu",
    pending: "Nemarcați",
    rate: "Rată",
    today: "Azi",
    chartTitle: "Ultimele 10 zile lucrătoare",
    chartHint: "Rata celor prezenți, întârziați sau remote. Concediul nu intră în calcul.",
    briefTitle: "Pe scurt",
    briefEmpty: "Registrul arată stabil în fereastra analizată.",
    openInsights: "Deschide analiza",
    todayList: "Situația de azi",
    markRest: "Marchează nemarcații",
    attendanceLead: "O singură stare pe persoană. Schimbarea se salvează imediat.",
    saved: "Salvat în browser",
    previous: "Ziua anterioară",
    next: "Ziua următoare",
    allDepartments: "Toate departamentele",
    onlyPending: "Doar nemarcați",
    clear: "Șterge",
    checkIn: "Intrare",
    checkOut: "Ieșire",
    note: "Notă",
    notePlaceholder: "Opțional",
    emptyFilter: "Nimeni nu corespunde filtrului.",
    teamLead: "Oamenii și departamentele folosite în registru.",
    addPerson: "Adaugă om",
    savePerson: "Salvează",
    updatePerson: "Actualizează",
    cancel: "Renunță",
    edit: "Editează",
    remove: "Șterge",
    confirmRemove: "Confirmă ștergerea",
    name: "Nume",
    role: "Rol",
    department: "Departament",
    email: "Email",
    nameError: "Numele este obligatoriu.",
    emailError: "Emailul nu pare valid.",
    lastWindow: "Ultimele 10 zile",
    noPeople: "Echipa este goală.",
    addFromTeam: "Adaugă pe cineva în echipă",
    askTitle: "Întreabă registrul",
    askHint: "Răspunsul iese din datele salvate, nu dintr-un model extern.",
    askPlaceholder: "Ex. Cine a întârziat des?",
    ask: "Întreabă",
    suggestions: ["Cine a întârziat des?", "Cum stă Vânzările?", "Cine lipsește azi?", "Rata Dianei Lungu", "Rata echipei"],
    insightsLead: "Semnale din ultimele zile lucrătoare și din prezența de azi.",
    noInsights: "Niciun semnal peste pragurile curente.",
    reportsLead: "Totaluri pe interval. Exportul CSV se deschide în Excel.",
    from: "De la",
    to: "Până la",
    export: "Descarcă CSV",
    rows: "Înregistrări",
    attended: "La program",
    person: "Persoană",
    emptyRange: "Nu există înregistrări în interval.",
    demo: "Date demonstrative",
  },
  en: {
    product: "AI Attendance Manager",
    version: "V9",
    orgHint: "Local register",
    navDashboard: "Board",
    navAttendance: "Attendance",
    navTeam: "Team",
    navInsights: "Insights",
    navReports: "Reports",
    language: "Language",
    stored: "Data stays in this browser.",
    reset: "Reload demo",
    greetingMorning: "Good morning",
    greetingAfternoon: "Good afternoon",
    greetingEvening: "Good evening",
    peopleCount: (n: number) => `${n} people`,
    present: "Present",
    late: "Late",
    absent: "Absent",
    remote: "Remote",
    leave: "Leave",
    pending: "Unmarked",
    rate: "Rate",
    today: "Today",
    chartTitle: "Last 10 workdays",
    chartHint: "Share of present, late, or remote. Leave is left out of the rate.",
    briefTitle: "In short",
    briefEmpty: "The register looks steady in the window we checked.",
    openInsights: "Open insights",
    todayList: "Today",
    markRest: "Mark unmarked present",
    attendanceLead: "One status per person. Changes save immediately.",
    saved: "Saved in the browser",
    previous: "Previous day",
    next: "Next day",
    allDepartments: "All departments",
    onlyPending: "Unmarked only",
    clear: "Clear",
    checkIn: "In",
    checkOut: "Out",
    note: "Note",
    notePlaceholder: "Optional",
    emptyFilter: "Nobody matches this filter.",
    teamLead: "People and departments used by the register.",
    addPerson: "Add person",
    savePerson: "Save",
    updatePerson: "Update",
    cancel: "Cancel",
    edit: "Edit",
    remove: "Delete",
    confirmRemove: "Confirm delete",
    name: "Name",
    role: "Role",
    department: "Department",
    email: "Email",
    nameError: "Name is required.",
    emailError: "That email does not look valid.",
    lastWindow: "Last 10 workdays",
    noPeople: "The team is empty.",
    addFromTeam: "Add someone to the team",
    askTitle: "Ask the register",
    askHint: "Answers come from the saved records, not from an external model.",
    askPlaceholder: "e.g. Who has been late?",
    ask: "Ask",
    suggestions: ["Who has been late?", "How is Vânzări doing?", "Who is missing today?", "Diana Lungu rate", "Team rate"],
    insightsLead: "Signals from recent workdays and from today.",
    noInsights: "Nothing is over the current thresholds.",
    reportsLead: "Totals for a date range. The CSV export opens in Excel.",
    from: "From",
    to: "To",
    export: "Download CSV",
    rows: "Records",
    attended: "Attended",
    person: "Person",
    emptyRange: "No records in this range.",
    demo: "Demo data",
  },
} as const;

export function statusLabel(lang: Lang, status: Status | "pending"): string {
  return copy[lang][status];
}

export function formatPercent(rate: number | null, lang: Lang): string {
  if (rate === null) return "—";
  return new Intl.NumberFormat(lang === "ro" ? "ro-RO" : "en-GB", {
    style: "percent",
    maximumFractionDigits: 0,
  }).format(rate);
}

export function formatLongDate(iso: string, lang: Lang): string {
  return new Intl.DateTimeFormat(lang === "ro" ? "ro-RO" : "en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(parseLocal(iso));
}

export function formatShortDate(iso: string, lang: Lang): string {
  return new Intl.DateTimeFormat(lang === "ro" ? "ro-RO" : "en-GB", {
    day: "numeric",
    month: "short",
  }).format(parseLocal(iso));
}

function parseLocal(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, (m ?? 1) - 1, d ?? 1);
}

export function greeting(lang: Lang, hour: number): string {
  if (hour < 12) return copy[lang].greetingMorning;
  if (hour < 18) return copy[lang].greetingAfternoon;
  return copy[lang].greetingEvening;
}

function personName(people: Person[], id: string): string {
  return people.find((person) => person.id === id)?.name ?? id;
}

export function insightCopy(lang: Lang, insight: Insight, people: Person[]): { title: string; body: string } {
  const name = "personId" in insight ? personName(people, insight.personId) : "";
  if (lang === "ro") {
    switch (insight.kind) {
      case "chronic-late":
        return {
          title: "Întârzieri repetate",
          body: `${name} a întârziat de ${insight.count} ori în ultimele ${insight.window} zile lucrătoare.`,
        };
      case "absence-cluster":
        return {
          title: "Absențe apropiate",
          body: `${name} are ${insight.count} absențe în ultimele ${insight.window} zile lucrătoare.`,
        };
      case "low-department":
        return {
          title: "Prezență slabă în departament",
          body: `${insight.department} stă la ${formatPercent(insight.rate, lang)} în ultimele ${insight.window} zile lucrătoare.`,
        };
      case "streak":
        return {
          title: "Serie curată",
          body: `${name} a fost la program ${insight.days} zile lucrătoare la rând.`,
        };
      case "remote-heavy":
        return {
          title: "Remote frecvent",
          body: `${name} a lucrat remote în ${insight.count} din ${insight.window} zile lucrătoare.`,
        };
      case "coverage-gap":
        return {
          title: "Acoperire subțire azi",
          body: `${insight.department}: ${insight.absent} din ${insight.total} sunt absenți azi.`,
        };
    }
  }
  switch (insight.kind) {
    case "chronic-late":
      return {
        title: "Repeated lateness",
        body: `${name} was late ${insight.count} times in the last ${insight.window} workdays.`,
      };
    case "absence-cluster":
      return {
        title: "Clustered absences",
        body: `${name} has ${insight.count} absences in the last ${insight.window} workdays.`,
      };
    case "low-department":
      return {
        title: "Low department attendance",
        body: `${insight.department} is at ${formatPercent(insight.rate, lang)} over the last ${insight.window} workdays.`,
      };
    case "streak":
      return {
        title: "Clean streak",
        body: `${name} has been in for ${insight.days} workdays in a row.`,
      };
    case "remote-heavy":
      return {
        title: "Often remote",
        body: `${name} worked remote on ${insight.count} of the last ${insight.window} workdays.`,
      };
    case "coverage-gap":
      return {
        title: "Thin coverage today",
        body: `${insight.department}: ${insight.absent} of ${insight.total} are absent today.`,
      };
  }
}

export function answerCopy(lang: Lang, answer: Answer, people: Person[]): string {
  const name = (id: string) => personName(people, id);
  if (lang === "ro") {
    switch (answer.type) {
      case "person":
        return `${name(answer.personId)}: prezență ${formatPercent(answer.rate, lang)} în ultimele 10 zile lucrătoare. ${answer.stats.present} la timp, ${answer.stats.late} întârzieri, ${answer.stats.absent} absențe, ${answer.stats.remote} remote, ${answer.stats.leave} concedii.`;
      case "department":
        return `${answer.department}: prezență ${formatPercent(answer.rate, lang)} în ultimele 10 zile lucrătoare. ${answer.stats.late} întârzieri, ${answer.stats.absent} absențe, ${answer.stats.remote} zile remote.`;
      case "today":
        return `Azi: ${answer.stats.present} prezenți, ${answer.stats.late} întârziați, ${answer.stats.absent} absenți, ${answer.stats.remote} remote, ${answer.stats.leave} în concediu, ${answer.stats.pending} nemarcați.`;
      case "late-list":
        if (answer.rows.length === 0) return `Nimeni nu a întârziat în ultimele ${answer.window} zile lucrătoare.`;
        return `Întârzieri în ultimele ${answer.window} zile lucrătoare: ${answer.rows.map((row) => `${name(row.personId)} (${row.count})`).join(", ")}.`;
      case "absences":
        if (answer.rows.length === 0) return `Nicio absență între ${formatShortDate(answer.from, lang)} și ${formatShortDate(answer.to, lang)}.`;
        return `Absențe din ${formatShortDate(answer.from, lang)} până în ${formatShortDate(answer.to, lang)}: ${answer.rows.map((row) => `${name(row.personId)} (${row.count})`).join(", ")}.`;
      case "company-rate":
        return `Rata echipei este ${formatPercent(answer.rate, lang)} între ${formatShortDate(answer.from, lang)} și ${formatShortDate(answer.to, lang)}.`;
      case "help":
        return "Pot răspunde despre o persoană, un departament, ziua de azi, întârzieri, absențe sau rata echipei.";
    }
  }
  switch (answer.type) {
    case "person":
      return `${name(answer.personId)}: ${formatPercent(answer.rate, lang)} attendance over the last 10 workdays. ${answer.stats.present} on time, ${answer.stats.late} late, ${answer.stats.absent} absent, ${answer.stats.remote} remote, ${answer.stats.leave} on leave.`;
    case "department":
      return `${answer.department}: ${formatPercent(answer.rate, lang)} attendance over the last 10 workdays. ${answer.stats.late} late marks, ${answer.stats.absent} absences, ${answer.stats.remote} remote days.`;
    case "today":
      return `Today: ${answer.stats.present} present, ${answer.stats.late} late, ${answer.stats.absent} absent, ${answer.stats.remote} remote, ${answer.stats.leave} on leave, ${answer.stats.pending} unmarked.`;
    case "late-list":
      if (answer.rows.length === 0) return `Nobody was late in the last ${answer.window} workdays.`;
      return `Lateness over the last ${answer.window} workdays: ${answer.rows.map((row) => `${name(row.personId)} (${row.count})`).join(", ")}.`;
    case "absences":
      if (answer.rows.length === 0) return `No absences from ${formatShortDate(answer.from, lang)} to ${formatShortDate(answer.to, lang)}.`;
      return `Absences from ${formatShortDate(answer.from, lang)} to ${formatShortDate(answer.to, lang)}: ${answer.rows.map((row) => `${name(row.personId)} (${row.count})`).join(", ")}.`;
    case "company-rate":
      return `Team attendance is ${formatPercent(answer.rate, lang)} from ${formatShortDate(answer.from, lang)} to ${formatShortDate(answer.to, lang)}.`;
    case "help":
      return "Ask about a person, a department, today, lateness, absences, or the team rate.";
  }
}
