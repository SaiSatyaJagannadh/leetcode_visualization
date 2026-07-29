import Link from "next/link";
import { getIndex } from "@/lib/traces";

export default function Home() {
  const { patterns, problems } = getIndex();
  const done = problems.filter((p) => p.ready).length;

  return (
    <main>
      <h1 className="brand">LeetViz</h1>
      <p className="tagline">
        Step through the algorithm, one line at a time. {done} of {problems.length}{" "}
        problems traced across {patterns.length} patterns.{" "}
        <Link href="/solve">Trace one of your own →</Link>
      </p>

      {patterns.map((pattern) => {
        const group = problems.filter((p) => p.pattern === pattern);
        const ready = group.filter((p) => p.ready).length;
        return (
          // <details> gives collapsible topics with no JS and no hydration cost.
          <details className="group" key={pattern}>
            <summary>
              <span className="chev" aria-hidden="true">
                ▸
              </span>
              <h2>{pattern}</h2>
              <span className="progress">
                {ready} / {group.length}
              </span>
            </summary>
            <div className="list">
              {group.map((p) =>
                p.ready ? (
                  <Link href={`/p/${p.slug}`} key={p.slug}>
                    <span className="num">{p.leetcode}</span>
                    <span>{p.title}</span>
                    <span className={`tag ${p.difficulty}`}>{p.difficulty}</span>
                  </Link>
                ) : (
                  <span className="row pending" key={p.slug}>
                    <span className="num">{p.leetcode}</span>
                    <span>{p.title}</span>
                    <span className={`tag ${p.difficulty}`}>{p.difficulty}</span>
                  </span>
                )
              )}
            </div>
          </details>
        );
      })}
    </main>
  );
}
