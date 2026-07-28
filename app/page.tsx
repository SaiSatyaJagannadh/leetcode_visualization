import Link from "next/link";
import { getIndex } from "@/lib/traces";

export default function Home() {
  const problems = getIndex();
  return (
    <main>
      <h1 className="brand">LeetViz</h1>
      <p className="tagline">Step through the algorithm, one line at a time.</p>
      <div className="list">
        {problems.map((p) => (
          <Link href={`/p/${p.slug}`} key={p.slug}>
            <span className={`tag ${p.difficulty}`}>{p.difficulty}</span>
            <span>{p.title}</span>
            <span className="pat">{p.pattern}</span>
          </Link>
        ))}
      </div>
    </main>
  );
}
