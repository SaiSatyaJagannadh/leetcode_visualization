/** @type {import('next').NextConfig} */
export default {
  output: "export",
  images: { unoptimized: true },
  // A production build would otherwise clobber the running dev server's chunks.
  distDir: process.env.NEXT_DIST || ".next",
  // Pages serves this repo under /leetcode_visualization, but dev serves it at
  // the root. Only the deploy workflow sets BASE_PATH, so `pnpm dev` stays plain.
  basePath: process.env.BASE_PATH || undefined,
};
