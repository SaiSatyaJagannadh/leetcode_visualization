import Link from "next/link";
import Viewer from "@/components/Viewer";
import { getIndex, getProblem } from "@/lib/traces";

export const generateStaticParams = () => getIndex().map((p) => ({ slug: p.slug }));

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
      <Viewer problem={problem} />
    </main>
  );
}
