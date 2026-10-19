import assert from "node:assert/strict";
import test from "node:test";
import {
  addDays,
  answerQuestion,
  attendanceRate,
  buildInsights,
  dayStats,
  isWeekend,
  mondayOf,
  personError,
  removeRecord,
  seedState,
  todayISO,
  toCsv,
  upsertRecord,
  workdaysEnding,
} from "./engine.ts";

const FIXED = new Date(2026, 9, 19, 10, 30, 0);

test("todayISO uses the local calendar day", () => {
  assert.equal(todayISO(FIXED), "2026-10-19");
  assert.equal(todayISO(new Date(2026, 0, 5, 23, 30)), "2026-01-05");
});

test("workdaysEnding skips weekends and stays in order", () => {
  const days = workdaysEnding("2026-10-19", 12);
  assert.equal(days.length, 12);
  assert.equal(days[0], "2026-10-02");
  assert.equal(days.at(-1), "2026-10-19");
  assert.equal(days.every((day) => !isWeekend(day)), true);
  assert.deepEqual(
    [...days].sort(),
    days,
  );
});

test("mondayOf returns the Monday of the same week", () => {
  assert.equal(mondayOf("2026-10-19"), "2026-10-19");
  assert.equal(mondayOf("2026-10-18"), "2026-10-12");
  assert.equal(mondayOf("2026-10-16"), "2026-10-12");
});

test("seed history is weekday-only and today stays partly open", () => {
  const { people, records } = seedState(FIXED);
  assert.equal(people.length, 12);
  assert.equal(records.some((record) => isWeekend(record.date)), false);
  assert.equal(records.some((record) => record.date > "2026-10-19"), false);
  const today = dayStats(people, records, "2026-10-19");
  assert.equal(today.pending, 2);
  assert.equal(today.absent, 2);
  assert.equal(today.late, 1);
  assert.equal(today.present, 6);
  assert.equal(today.remote, 1);
  const past = records.filter((record) => record.date < "2026-10-19");
  assert.equal(past.every((record) => record.status === "absent" || record.status === "leave" || record.checkOut), true);
  assert.equal(
    records.filter((record) => record.date === "2026-10-19").every((record) => !record.checkOut),
    true,
  );
});

test("insights name the scripted attendance story", () => {
  const { people, records } = seedState(FIXED);
  const insights = buildInsights(people, records, "2026-10-19");
  const kinds = insights.map((insight) => insight.kind);
  assert.equal(kinds[0], "coverage-gap");
  assert.equal(
    insights.some((insight) => insight.kind === "chronic-late" && insight.personId === "p-vlad" && insight.count >= 3),
    true,
  );
  assert.equal(
    insights.some((insight) => insight.kind === "absence-cluster" && insight.personId === "p-mihai"),
    true,
  );
  assert.equal(
    insights.some((insight) => insight.kind === "absence-cluster" && insight.personId === "p-paul"),
    true,
  );
  assert.equal(
    insights.some((insight) => insight.kind === "low-department" && insight.department === "Vânzări"),
    true,
  );
  assert.equal(
    insights.some((insight) => insight.kind === "remote-heavy" && insight.personId === "p-ana"),
    true,
  );
  assert.equal(
    insights.some((insight) => insight.kind === "streak" && insight.personId === "p-diana"),
    true,
  );
  assert.equal(
    insights.some((insight) => insight.kind === "coverage-gap" && insight.department === "Vânzări"),
    true,
  );
});

test("upsert replaces the same person and day", () => {
  const first = upsertRecord([], { personId: "p-ana", date: "2026-10-19", status: "present", checkIn: "09:00" });
  assert.equal(first.length, 1);
  const next = upsertRecord(first, { personId: "p-ana", date: "2026-10-19", status: "remote", checkIn: "09:10" });
  assert.equal(next.length, 1);
  assert.equal(next[0]?.status, "remote");
  assert.equal(removeRecord(next, "p-ana", "2026-10-19").length, 0);
});

test("questions resolve people, departments, today, and lates", () => {
  const { people, records } = seedState(FIXED);
  const diana = answerQuestion("Rata Dianei Lungu", people, records, "2026-10-19");
  assert.equal(diana.type, "person");
  if (diana.type === "person") {
    assert.equal(diana.personId, "p-diana");
    assert.equal(diana.rate, 1);
  }

  const sales = answerQuestion("Cum stă Vânzările?", people, records, "2026-10-19");
  assert.equal(sales.type, "department");
  if (sales.type === "department") {
    assert.equal(sales.department, "Vânzări");
    assert.ok(sales.rate < 0.82);
  }

  const today = answerQuestion("Cine lipsește azi?", people, records, "2026-10-19");
  assert.equal(today.type, "today");
  if (today.type === "today") assert.equal(today.stats.absent, 2);

  const lates = answerQuestion("Cine a întârziat des?", people, records, "2026-10-19");
  assert.equal(lates.type, "late-list");
  if (lates.type === "late-list") {
    assert.equal(lates.rows[0]?.personId, "p-vlad");
    assert.ok((lates.rows[0]?.count ?? 0) >= 3);
  }

  assert.equal(answerQuestion("   ", people, records, "2026-10-19").type, "help");
  assert.equal(answerQuestion("ce facem la prânz?", people, records, "2026-10-19").type, "help");
});

test("csv escapes commas and stays inside the range", () => {
  const people = [
    { id: "p1", name: "Popescu, Ana", role: "Lead", department: "Design", email: "ana@example.com" },
  ];
  const records = [
    { personId: "p1", date: "2026-10-01", status: "present" as const, checkIn: "08:40", note: 'nota "x"' },
    { personId: "p1", date: "2026-10-20", status: "absent" as const },
  ];
  const csv = toCsv(people, records, "2026-10-01", "2026-10-16");
  assert.match(csv, /^date,name,department/);
  assert.match(csv, /"Popescu, Ana"/);
  assert.match(csv, /"nota ""x"""/);
  assert.equal(csv.includes("2026-10-20"), false);
});

test("person validation and rate math", () => {
  assert.equal(personError({ name: "  ", email: "" }), "name");
  assert.equal(personError({ name: "Ana", email: "nu-i-email" }), "email");
  assert.equal(personError({ name: "Ana", email: "ana@atelier.ro" }), null);
  assert.equal(attendanceRate({ present: 1, late: 1, remote: 1, absent: 1, leave: 4 }), 0.75);
  assert.equal(attendanceRate({ present: 0, late: 0, remote: 0, absent: 0, leave: 2 }), null);
  assert.equal(addDays("2026-10-19", -1), "2026-10-18");
});
