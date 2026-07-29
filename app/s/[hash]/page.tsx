import type { Metadata } from "next";
import Link from "next/link";
import { SharedTrace } from "@/components/Solve";

export const metadata: Metadata = {
  title: "Shared trace — LeetViz",
  robots: { index: false, follow: false },
};

export default async function Shared({ params }: { params: Promise<{ hash: string }> }) {
  const { hash } = await params;
  return (
    <main>
      <Link className="crumb" href="/solve">
        ← trace another
      </Link>
      <h1>Shared trace</h1>
      <SharedTrace hash={hash} />
    </main>
  );
}
