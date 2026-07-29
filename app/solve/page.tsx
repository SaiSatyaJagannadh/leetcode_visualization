import type { Metadata } from "next";
import Link from "next/link";
import { SolveForm } from "@/components/Solve";

// Generated traces are not library content; keeping them out of the index keeps
// the crawlable surface to the 150 authored problems.
export const metadata: Metadata = {
  title: "Trace a problem — LeetViz",
  robots: { index: false, follow: false },
};

export default function Solve() {
  return (
    <main>
      <Link className="crumb" href="/">
        ← all problems
      </Link>
      <h1>Trace a problem</h1>
      <p className="tagline">
        Describe a problem and get the same step-through player the authored problems use.
      </p>
      <SolveForm />
    </main>
  );
}
