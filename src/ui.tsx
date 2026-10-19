import { colorFor, initials } from "./engine";

export function Avatar({ name, id }: { name: string; id: string }) {
  return (
    <span className="avatar" style={{ background: colorFor(id) }} aria-hidden="true">
      {initials(name)}
    </span>
  );
}
