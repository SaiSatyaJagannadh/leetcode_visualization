/** @type {import('next').NextConfig} */
export default {
  // No `output: "export"` — the target is Vercel, which prerenders the static
  // pages at build time and runs /api/*.py as Python functions alongside them.
  // No `basePath` either: that existed only for the GitHub Pages subpath.
  images: { unoptimized: true },
  // A production build would otherwise clobber the running dev server's chunks.
  distDir: process.env.NEXT_DIST || ".next",
};
