/** @type {import('next').NextConfig} */
export default {
  output: "export",
  images: { unoptimized: true },
  // A production build would otherwise clobber the running dev server's chunks.
  distDir: process.env.NEXT_DIST || ".next",
};
