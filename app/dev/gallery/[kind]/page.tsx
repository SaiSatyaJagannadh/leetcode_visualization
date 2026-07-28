import Link from "next/link";
import Viewer from "@/components/Viewer";
import { getFixture, getFixtureNames } from "@/lib/traces";

export const generateStaticParams = () => getFixtureNames().map((kind) => ({ kind }));

/** One fixture at a time — the gallery is for comparing, this is for debugging. */
export default async function One({ params }: { params: Promise<{ kind: string }> }) {
  const { kind } = await params;
  const fixture = getFixture(kind);
  return (
    <main>
      <Link className="crumb" href="/dev/gallery">
        ← gallery
      </Link>
      <h1>{fixture.title}</h1>
      <Viewer problem={fixture} />
    </main>
  );
}
