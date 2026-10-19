export type Status = "present" | "late" | "absent" | "remote" | "leave";

export type Person = {
  id: string;
  name: string;
  role: string;
  department: string;
  email: string;
};

export type AttendanceRecord = {
  personId: string;
  date: string;
  status: Status;
  checkIn?: string;
  checkOut?: string;
  note?: string;
};

export type Insight =
  | { kind: "chronic-late"; personId: string; count: number; window: number }
  | { kind: "absence-cluster"; personId: string; count: number; window: number }
  | { kind: "low-department"; department: string; rate: number; window: number }
  | { kind: "streak"; personId: string; days: number }
  | { kind: "remote-heavy"; personId: string; count: number; window: number }
  | { kind: "coverage-gap"; department: string; absent: number; total: number };

export type StatusCounts = Record<Status, number>;

export type DayStats = StatusCounts & { pending: number; total: number };

export type Answer =
  | { type: "person"; personId: string; stats: StatusCounts; rate: number }
  | { type: "department"; department: string; stats: StatusCounts; rate: number }
  | { type: "today"; stats: DayStats }
  | { type: "late-list"; rows: { personId: string; count: number }[]; window: number }
  | { type: "absences"; rows: { personId: string; count: number }[]; from: string; to: string }
  | { type: "company-rate"; rate: number; from: string; to: string }
  | { type: "help" };

export const DEMO_ORG = "Atelier Nord";
export const DEPARTMENTS = [
  "Inginerie",
  "Design",
  "Resurse umane",
  "Vânzări",
  "Operațiuni",
  "Finanțe",
] as const;

const HISTORY_DAYS = 12;
const LOOKBACK = 10;

const PEOPLE: Person[] = [
  { id: "p-andrei", name: "Andrei Popescu", role: "Frontend", department: "Inginerie", email: "andrei.popescu@ateliernord.ro" },
  { id: "p-maria", name: "Maria Ionescu", role: "Backend", department: "Inginerie", email: "maria.ionescu@ateliernord.ro" },
  { id: "p-elena", name: "Elena Radu", role: "Product design", department: "Design", email: "elena.radu@ateliernord.ro" },
  { id: "p-vlad", name: "Vlad Dumitrescu", role: "QA", department: "Inginerie", email: "vlad.dumitrescu@ateliernord.ro" },
  { id: "p-ioana", name: "Ioana Stan", role: "People partner", department: "Resurse umane", email: "ioana.stan@ateliernord.ro" },
  { id: "p-mihai", name: "Mihai Georgescu", role: "Account", department: "Vânzări", email: "mihai.georgescu@ateliernord.ro" },
  { id: "p-ana", name: "Ana Pavel", role: "Account", department: "Vânzări", email: "ana.pavel@ateliernord.ro" },
  { id: "p-cristian", name: "Cristian Matei", role: "Coordonator", department: "Operațiuni", email: "cristian.matei@ateliernord.ro" },
  { id: "p-sofia", name: "Sofia Nistor", role: "Brand", department: "Design", email: "sofia.nistor@ateliernord.ro" },
  { id: "p-radu", name: "Radu Enache", role: "Tech lead", department: "Inginerie", email: "radu.enache@ateliernord.ro" },
  { id: "p-diana", name: "Diana Lungu", role: "Analist", department: "Finanțe", email: "diana.lungu@ateliernord.ro" },
  { id: "p-paul", name: "Paul Barbu", role: "Suport", department: "Operațiuni", email: "paul.barbu@ateliernord.ro" },
];

/** Oldest → newest, one status per past workday. Today is filled separately. */
const PATTERN: Record<string, Status[]> = {
  "p-andrei": ["present", "present", "present", "late", "present", "present", "present", "remote", "present", "present", "present", "present"],
  "p-maria": ["present", "present", "remote", "present", "present", "present", "present", "present", "present", "late", "present", "present"],
  "p-elena": ["present", "present", "present", "present", "leave", "present", "present", "present", "remote", "present", "present", "present"],
  "p-vlad": ["late", "present", "late", "present", "present", "late", "remote", "present", "late", "present", "present", "late"],
  "p-ioana": ["present", "late", "present", "present", "present", "present", "late", "present", "present", "present", "present", "present"],
  "p-mihai": ["present", "absent", "present", "absent", "absent", "present", "absent", "present", "absent", "present", "present", "absent"],
  "p-ana": ["remote", "present", "remote", "present", "remote", "remote", "present", "remote", "present", "remote", "present", "remote"],
  "p-cristian": ["present", "present", "present", "present", "present", "late", "present", "present", "present", "present", "remote", "present"],
  "p-sofia": ["present", "present", "present", "leave", "present", "present", "present", "present", "present", "present", "present", "remote"],
  "p-radu": ["present", "present", "present", "present", "present", "present", "late", "present", "present", "present", "present", "present"],
  "p-diana": ["present", "present", "present", "present", "present", "present", "present", "present", "present", "present", "present", "present"],
  "p-paul": ["present", "present", "present", "present", "remote", "present", "present", "present", "present", "present", "absent", "absent"],
};

const TODAY_PLAN: Record<string, Status | "pending"> = {
  "p-andrei": "present",
  "p-maria": "present",
  "p-elena": "remote",
  "p-vlad": "late",
  "p-ioana": "present",
  "p-mihai": "absent",
  "p-ana": "pending",
  "p-cristian": "present",
  "p-sofia": "pending",
  "p-radu": "present",
  "p-diana": "present",
  "p-paul": "absent",
};

export function todayISO(now = new Date()): string {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function parseISO(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, (m ?? 1) - 1, d ?? 1);
}

export function addDays(iso: string, days: number): string {
  const date = parseISO(iso);
  date.setDate(date.getDate() + days);
  return todayISO(date);
}

export function isWeekend(iso: string): boolean {
  const day = parseISO(iso).getDay();
  return day === 0 || day === 6;
}

/** Workdays ending at `endInclusive`, oldest first. */
export function workdaysEnding(endInclusive: string, count: number): string[] {
  const days: string[] = [];
  let cursor = endInclusive;
  while (days.length < count) {
    if (!isWeekend(cursor)) days.push(cursor);
    cursor = addDays(cursor, -1);
  }
  return days.reverse();
}

export function mondayOf(iso: string): string {
  const day = parseISO(iso).getDay();
  const diff = day === 0 ? -6 : 1 - day;
  return addDays(iso, diff);
}

export function emptyCounts(): StatusCounts {
  return { present: 0, late: 0, absent: 0, remote: 0, leave: 0 };
}

export function countStatuses(records: AttendanceRecord[]): StatusCounts {
  const counts = emptyCounts();
  for (const record of records) counts[record.status] += 1;
  return counts;
}

/** Share of marked days that were present, late, or remote. Leave is excluded. */
export function attendanceRate(counts: StatusCounts): number | null {
  const attended = counts.present + counts.late + counts.remote;
  const denom = attended + counts.absent;
  if (denom === 0) return null;
  return attended / denom;
}

export function recordsFor(people: Person[], records: AttendanceRecord[]): AttendanceRecord[] {
  const ids = new Set(people.map((person) => person.id));
  return records.filter((record) => ids.has(record.personId));
}

export function departmentsOf(people: Person[]): string[] {
  return [...new Set(people.map((person) => person.department))].sort((a, b) => a.localeCompare(b, "ro"));
}

export function sortPeople(people: Person[]): Person[] {
  return [...people].sort((a, b) => a.name.localeCompare(b.name, "ro"));
}

export function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

const PALETTE = ["#0e6b52", "#1e4f86", "#8a5a00", "#8e2f2a", "#3f5c4b", "#5d3f72"];

export function colorFor(id: string): string {
  let n = 0;
  for (const ch of id) n = (n + ch.charCodeAt(0)) % PALETTE.length;
  return PALETTE[n] ?? PALETTE[0];
}

export function defaultTimes(status: Status): { checkIn?: string; checkOut?: string } {
  if (status === "present") return { checkIn: "08:55" };
  if (status === "late") return { checkIn: "09:20" };
  if (status === "remote") return { checkIn: "09:00" };
  return {};
}

export function upsertRecord(records: AttendanceRecord[], next: AttendanceRecord): AttendanceRecord[] {
  const index = records.findIndex((record) => record.personId === next.personId && record.date === next.date);
  if (index === -1) return [...records, next];
  const copy = records.slice();
  copy[index] = next;
  return copy;
}

export function removeRecord(records: AttendanceRecord[], personId: string, date: string): AttendanceRecord[] {
  return records.filter((record) => !(record.personId === personId && record.date === date));
}

export function personError(input: { name: string; email: string }): "name" | "email" | null {
  if (!input.name.trim()) return "name";
  if (input.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email.trim())) return "email";
  return null;
}

export function createId(): string {
  return `p-${crypto.randomUUID()}`;
}

function clock(startMin: number, spread: number, salt: number): string {
  const mins = startMin + (Math.abs(salt) % spread);
  const hh = Math.floor(mins / 60);
  const mm = mins % 60;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function addMinutes(hhmm: string, minutes: number): string {
  const [h, m] = hhmm.split(":").map(Number);
  const total = (h ?? 0) * 60 + (m ?? 0) + minutes;
  const hh = Math.floor(total / 60) % 24;
  const mm = total % 60;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function timesFor(status: Status, salt: number, withCheckout: boolean): { checkIn?: string; checkOut?: string } {
  if (status === "absent" || status === "leave") return {};
  const checkIn =
    status === "late"
      ? clock(9 * 60 + 12, 55, salt)
      : status === "remote"
        ? clock(8 * 60 + 45, 30, salt)
        : clock(8 * 60 + 35, 25, salt);
  if (!withCheckout) return { checkIn };
  return { checkIn, checkOut: addMinutes(checkIn, 8 * 60 + 20 + (Math.abs(salt) % 35)) };
}

export function seedState(now = new Date()): { people: Person[]; records: AttendanceRecord[] } {
  const today = todayISO(now);
  const history = workdaysEnding(addDays(today, -1), HISTORY_DAYS);
  const people = PEOPLE.map((person) => ({ ...person }));
  const records: AttendanceRecord[] = [];

  people.forEach((person, personIndex) => {
    const pattern = PATTERN[person.id] ?? [];
    history.forEach((date, index) => {
      const status = pattern[index] ?? "present";
      const salt = personIndex * 17 + index * 3 + person.id.charCodeAt(person.id.length - 1);
      records.push({
        personId: person.id,
        date,
        status,
        ...timesFor(status, salt, true),
      });
    });

    const todayStatus = TODAY_PLAN[person.id] ?? "pending";
    if (todayStatus !== "pending") {
      const salt = personIndex * 13 + person.id.charCodeAt(2);
      records.push({
        personId: person.id,
        date: today,
        status: todayStatus,
        ...timesFor(todayStatus, salt, false),
      });
    }
  });

  return { people, records };
}

export function dayStats(people: Person[], records: AttendanceRecord[], date: string): DayStats {
  const known = recordsFor(people, records).filter((record) => record.date === date);
  const counts = countStatuses(known);
  return {
    ...counts,
    pending: Math.max(0, people.length - known.length),
    total: people.length,
  };
}

function streakDays(records: AttendanceRecord[], personId: string, pastOldestFirst: string[]): number {
  let streak = 0;
  for (let i = pastOldestFirst.length - 1; i >= 0; i -= 1) {
    const date = pastOldestFirst[i];
    const record = records.find((item) => item.personId === personId && item.date === date);
    if (!record || (record.status !== "present" && record.status !== "remote")) break;
    streak += 1;
  }
  return streak;
}

export function buildInsights(people: Person[], records: AttendanceRecord[], today = todayISO()): Insight[] {
  const history = recordsFor(people, records);
  const past = workdaysEnding(addDays(today, -1), LOOKBACK);
  const pastSet = new Set(past);
  const last5 = new Set(past.slice(-5));
  const insights: Insight[] = [];

  for (const person of people) {
    const mine = history.filter((record) => record.personId === person.id && pastSet.has(record.date));
    const late = mine.filter((record) => record.status === "late").length;
    if (late >= 3) insights.push({ kind: "chronic-late", personId: person.id, count: late, window: past.length });

    const recentAbsent = mine.filter((record) => last5.has(record.date) && record.status === "absent").length;
    if (recentAbsent >= 2) {
      insights.push({ kind: "absence-cluster", personId: person.id, count: recentAbsent, window: last5.size });
    }

    const remote = mine.filter((record) => record.status === "remote").length;
    if (remote >= 5) insights.push({ kind: "remote-heavy", personId: person.id, count: remote, window: past.length });

    const streak = streakDays(history, person.id, past);
    if (streak >= 8 && remote < 5) insights.push({ kind: "streak", personId: person.id, days: streak });
  }

  for (const department of departmentsOf(people)) {
    const members = people.filter((person) => person.department === department);
    const mine = history.filter(
      (record) => pastSet.has(record.date) && members.some((person) => person.id === record.personId),
    );
    const rate = attendanceRate(countStatuses(mine));
    if (rate !== null && rate < 0.8 && members.length >= 2) {
      insights.push({ kind: "low-department", department, rate, window: past.length });
    }

    const absentToday = history.filter(
      (record) =>
        record.date === today &&
        record.status === "absent" &&
        members.some((person) => person.id === record.personId),
    ).length;
    if (members.length >= 2 && absentToday / members.length >= 0.5) {
      insights.push({ kind: "coverage-gap", department, absent: absentToday, total: members.length });
    }
  }

  const order: Insight["kind"][] = [
    "coverage-gap",
    "absence-cluster",
    "chronic-late",
    "low-department",
    "remote-heavy",
    "streak",
  ];
  return insights.sort((a, b) => order.indexOf(a.kind) - order.indexOf(b.kind));
}

function norm(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase();
}

function hasWord(haystack: string, word: string): boolean {
  const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?:^|[^a-z0-9])${escaped}(?:[^a-z0-9]|$)`).test(haystack);
}

function findPerson(question: string, people: Person[]): Person | undefined {
  const q = norm(question);
  return people.find((person) => {
    const name = norm(person.name);
    if (q.includes(name)) return true;
    const [first = "", last = ""] = name.split(" ");
    return (first.length >= 4 && hasWord(q, first)) || (last.length >= 4 && hasWord(q, last));
  });
}

function statsIn(peopleIds: Set<string>, records: AttendanceRecord[], dates: Set<string>): StatusCounts {
  return countStatuses(records.filter((record) => peopleIds.has(record.personId) && dates.has(record.date)));
}

export function answerQuestion(
  question: string,
  people: Person[],
  records: AttendanceRecord[],
  today = todayISO(),
): Answer {
  const q = norm(question.trim());
  if (!q) return { type: "help" };
  const history = recordsFor(people, records);
  const person = findPerson(question, people);
  const past = workdaysEnding(addDays(today, -1), LOOKBACK);
  const pastSet = new Set(past);

  if (person) {
    const stats = statsIn(new Set([person.id]), history, pastSet);
    return { type: "person", personId: person.id, stats, rate: attendanceRate(stats) ?? 0 };
  }

  const department = departmentsOf(people).find((name) => q.includes(norm(name)));
  if (department) {
    const ids = new Set(people.filter((item) => item.department === department).map((item) => item.id));
    const stats = statsIn(ids, history, pastSet);
    return { type: "department", department, stats, rate: attendanceRate(stats) ?? 0 };
  }

  if (/(azi|astazi|today)/.test(q)) {
    return { type: "today", stats: dayStats(people, history, today) };
  }

  if (/(intarz|late)/.test(q)) {
    const rows = people
      .map((item) => ({
        personId: item.id,
        count: history.filter((record) => record.personId === item.id && pastSet.has(record.date) && record.status === "late")
          .length,
      }))
      .filter((row) => row.count > 0)
      .sort((a, b) => b.count - a.count);
    return { type: "late-list", rows, window: past.length };
  }

  if (/(absen|lipsa|lipsesc|missing)/.test(q)) {
    const from = mondayOf(today);
    const dates = new Set<string>();
    for (let cursor = from; cursor <= today; cursor = addDays(cursor, 1)) dates.add(cursor);
    const rows = people
      .map((item) => ({
        personId: item.id,
        count: history.filter((record) => record.personId === item.id && dates.has(record.date) && record.status === "absent")
          .length,
      }))
      .filter((row) => row.count > 0)
      .sort((a, b) => b.count - a.count);
    return { type: "absences", rows, from, to: today };
  }

  if (/(rata|rate|procent|percent)/.test(q)) {
    const stats = statsIn(new Set(people.map((item) => item.id)), history, pastSet);
    return { type: "company-rate", rate: attendanceRate(stats) ?? 0, from: past[0] ?? today, to: past[past.length - 1] ?? today };
  }

  return { type: "help" };
}

function csvEscape(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replace(/"/g, '""')}"`;
  return value;
}

export function toCsv(people: Person[], records: AttendanceRecord[], from: string, to: string): string {
  const header = ["date", "name", "department", "role", "status", "check_in", "check_out", "note"];
  const byId = new Map(people.map((person) => [person.id, person]));
  const lines = [header.join(",")];
  const filtered = recordsFor(people, records)
    .filter((record) => record.date >= from && record.date <= to)
    .sort((a, b) => a.date.localeCompare(b.date) || (byId.get(a.personId)?.name ?? "").localeCompare(byId.get(b.personId)?.name ?? "", "ro"));

  for (const record of filtered) {
    const person = byId.get(record.personId);
    if (!person) continue;
    lines.push(
      [record.date, person.name, person.department, person.role, record.status, record.checkIn ?? "", record.checkOut ?? "", record.note ?? ""]
        .map(csvEscape)
        .join(","),
    );
  }
  return lines.join("\n");
}

export type ReportRow = { person: Person; stats: StatusCounts; rate: number | null };

export function reportRows(people: Person[], records: AttendanceRecord[], from: string, to: string): ReportRow[] {
  const known = recordsFor(people, records).filter((record) => record.date >= from && record.date <= to);
  return sortPeople(people).map((person) => {
    const stats = countStatuses(known.filter((record) => record.personId === person.id));
    return { person, stats, rate: attendanceRate(stats) };
  });
}
