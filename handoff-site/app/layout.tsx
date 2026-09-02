import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CIV 2026 Data Hackathon — Internal Handoff",
  description: "Strategy, tactics, operations and attendee experience for the CIV 2026 Data Hackathon.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
