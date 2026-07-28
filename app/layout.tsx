import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LeetViz",
  description: "Step through the algorithm, one line at a time.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
