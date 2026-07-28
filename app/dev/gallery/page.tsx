import Link from "next/link";
import Viewer from "@/components/Viewer";
import { getFixture, getFixtureNames } from "@/lib/traces";

/** Every renderer side by side, driven only by fixtures. No real content here. */
export default function Gallery() {
  const fixtures = getFixtureNames().map(getFixture);
  return (
    <main>
      <Link className="crumb" href="/">
        ← all problems
      </Link>
      <h1 className="brand">Renderer gallery</h1>
      <p className="tagline">
        {fixtures.length} fixtures exercising every op the schema supports. If a renderer
        breaks, it breaks here first.
      </p>
      {fixtures.map((f) => (
        <section className="gallery-item" key={f.slug}>
          <h2>{f.title}</h2>
          <Viewer problem={f} keys={false} />
        </section>
      ))}
    </main>
  );
}
