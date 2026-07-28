import type { Val } from "@/lib/schema";

/** Which cell of which array each pointer variable is currently on. */
export type Pointers = Record<string, { name: string; index: number }[]>;

function show(v: Val): string {
  if (v === null) return "null";
  if (typeof v === "string") return v;
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export function ArrayView({
  name,
  value,
  pointers,
  hit,
}: {
  name: string;
  value: Val[];
  pointers: { name: string; index: number }[];
  hit: boolean;
}) {
  return (
    <div className={hit ? "var hit" : "var"}>
      <span className="name">{name}</span>
      {value.length === 0 ? (
        <span className="empty-note">empty</span>
      ) : (
        <div className="cells">
          {value.map((v, i) => {
            const on = pointers.filter((p) => p.index === i);
            return (
              <div className={on.length ? "cell hit" : "cell"} key={i}>
                <span className="box">{show(v)}</span>
                <span className="idx">{i}</span>
                <span className="ptrs">{on.map((p) => p.name).join(" ")}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function MapView({
  name,
  value,
  changed,
  hit,
}: {
  name: string;
  value: Record<string, Val>;
  changed: Set<string>;
  hit: boolean;
}) {
  const entries = Object.entries(value);
  return (
    <div className={hit ? "var hit" : "var"}>
      <span className="name">{name}</span>
      {entries.length === 0 ? (
        <span className="empty-note">empty</span>
      ) : (
        <div className="kv">
          {entries.map(([k, v]) => (
            <span className={changed.has(k) ? "pair hit" : "pair"} key={k}>
              <span className="k">{k}</span> → {show(v)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export function ScalarView({
  entries,
  hits,
}: {
  entries: [string, Val][];
  hits: Set<string>;
}) {
  if (!entries.length) return null;
  return (
    <div className="var">
      <div className="scalars">
        {entries.map(([k, v]) => (
          <span className={hits.has(k) ? "chip hit" : "chip"} key={k}>
            <span className="k">{k} = </span>
            {show(v)}
          </span>
        ))}
      </div>
    </div>
  );
}
