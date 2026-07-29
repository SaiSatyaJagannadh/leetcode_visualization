import type { Metadata } from "next";
import { SpendDash } from "@/components/Solve";

export const metadata: Metadata = {
  title: "Spend — LeetViz",
  robots: { index: false, follow: false },
};

export default function Spend() {
  return (
    <main>
      <h1>Spend</h1>
      <p className="tagline">
        Live counters from KV — no estimates. The API refuses without the shared secret.
      </p>
      <SpendDash />
    </main>
  );
}
