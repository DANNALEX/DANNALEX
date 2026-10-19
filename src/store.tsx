import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  defaultTimes,
  removeRecord,
  seedState,
  upsertRecord,
  type AttendanceRecord,
  type Person,
} from "./engine";
import type { Lang } from "./i18n";

const KEY = "aam-v9";

type Persisted = {
  v: 1;
  people: Person[];
  records: AttendanceRecord[];
  lang: Lang;
};

type Store = Persisted & {
  setLang: (lang: Lang) => void;
  reset: () => void;
  upsert: (record: AttendanceRecord) => void;
  clearMark: (personId: string, date: string) => void;
  markUnmarkedPresent: (date: string) => void;
  savePerson: (person: Person) => void;
  deletePerson: (id: string) => void;
};

const StoreContext = createContext<Store | null>(null);

function isPerson(value: unknown): value is Person {
  if (!value || typeof value !== "object") return false;
  const person = value as Person;
  return (
    typeof person.id === "string" &&
    typeof person.name === "string" &&
    typeof person.role === "string" &&
    typeof person.department === "string" &&
    typeof person.email === "string"
  );
}

function isRecord(value: unknown): value is AttendanceRecord {
  if (!value || typeof value !== "object") return false;
  const record = value as AttendanceRecord;
  return (
    typeof record.personId === "string" &&
    typeof record.date === "string" &&
    (record.status === "present" ||
      record.status === "late" ||
      record.status === "absent" ||
      record.status === "remote" ||
      record.status === "leave")
  );
}

function fresh(lang: Lang = "ro"): Persisted {
  return { v: 1, ...seedState(), lang };
}

function load(): Persisted {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return fresh();
    const parsed = JSON.parse(raw) as Partial<Persisted>;
    if (parsed.v !== 1 || !Array.isArray(parsed.people) || !Array.isArray(parsed.records)) return fresh();
    if (!parsed.people.every(isPerson) || !parsed.records.every(isRecord)) return fresh();
    return {
      v: 1,
      people: parsed.people,
      records: parsed.records,
      lang: parsed.lang === "en" ? "en" : "ro",
    };
  } catch {
    return fresh();
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<Persisted>(load);

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(state));
    document.documentElement.lang = state.lang;
  }, [state]);

  const store = useMemo<Store>(() => {
    return {
      ...state,
      setLang: (lang) => setState((current) => ({ ...current, lang })),
      reset: () => setState((current) => fresh(current.lang)),
      upsert: (record) => setState((current) => ({ ...current, records: upsertRecord(current.records, record) })),
      clearMark: (personId, date) =>
        setState((current) => ({ ...current, records: removeRecord(current.records, personId, date) })),
      markUnmarkedPresent: (date) =>
        setState((current) => {
          const marked = new Set(current.records.filter((record) => record.date === date).map((record) => record.personId));
          let records = current.records;
          for (const person of current.people) {
            if (marked.has(person.id)) continue;
            const times = defaultTimes("present");
            records = upsertRecord(records, { personId: person.id, date, status: "present", ...times });
          }
          return { ...current, records };
        }),
      savePerson: (person) =>
        setState((current) => {
          const exists = current.people.some((item) => item.id === person.id);
          const people = exists
            ? current.people.map((item) => (item.id === person.id ? person : item))
            : [...current.people, person];
          return { ...current, people };
        }),
      deletePerson: (id) =>
        setState((current) => ({
          ...current,
          people: current.people.filter((person) => person.id !== id),
          records: current.records.filter((record) => record.personId !== id),
        })),
    };
  }, [state]);

  return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>;
}

export function useStore(): Store {
  const store = useContext(StoreContext);
  if (!store) throw new Error("Store missing");
  return store;
}
