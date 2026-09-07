import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EXtendQuality | Intelligent Bearing Inspection",
  description: "Industrial AI quality intelligence for bearing manufacturing.",
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
