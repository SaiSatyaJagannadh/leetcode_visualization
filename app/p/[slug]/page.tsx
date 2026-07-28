import Link from "next/link";
import Viewer from "@/components/Viewer";
import { getIndex, getProblem } from "@/lib/traces";

export const generateStaticParams = () =>
  getIndex()
    .problems.filter((p) => p.ready)
    .map((p) => ({ slug: p.slug }));

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const problem = getProblem((await params).slug);
  return (
    <main>
      <Link className="crumb" href="/">
        ← all problems
      </Link>
      <h1>{problem.title}</h1>
      <div className="meta">
        <span className={`tag ${problem.difficulty}`}>{problem.difficulty}</span>
        <span className="tag">{problem.pattern}</span>
        <span className="tag">LeetCode {problem.leetcode}</span>
      </div>
      <p className="prompt">{problem.prompt}</p>

      {problem.examples.length > 0 && (
        <div className="examples">
          {problem.examples.map((ex, i) => (
            <div className="example" key={i}>
              <div>
                <span className="lbl">in </span>
                {ex.input}
              </div>
              <div>
                <span className="lbl">out </span>
                {ex.output}
              </div>
              {ex.why && <div className="why">{ex.why}</div>}
            </div>
          ))}
        </div>
      )}

      {problem.constraints.length > 0 && (
        <ul className="constraints">
          {problem.constraints.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      )}

      <Viewer problem={problem} />
    </main>
  );
}
