/** @type {import('next').NextConfig} */
export default {
  // No `output: "export"` — the target is Vercel, which prerenders the static
  // pages at build time and runs /api/*.py as Python functions alongside them.
  // No `basePath` either: that existed only for the GitHub Pages subpath.
  images: { unoptimized: true },
  // A production build would otherwise clobber the running dev server's chunks.
  distDir: process.env.NEXT_DIST || ".next",
  // `next dev` has no Python runtime, so api/*.py 404s and /solve looks broken.
  // In dev only, proxy to pipeline/devserver.py, which mounts those exact
  // handler classes. Vercel serves them natively in production, so this rewrite
  // must never apply there — hence the NODE_ENV guard.
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    const port = process.env.DEV_API_PORT || "8787";
    return [{ source: "/api/:path*", destination: `http://127.0.0.1:${port}/api/:path*` }];
  },
  // A generation runs ~40s. The dev proxy defaults to 30s and returns a 500
  // while Python is still working, which reads as "generation is broken" when
  // it actually succeeded and cached.
  experimental: { proxyTimeout: 300_000 },
};
