import type { Metadata } from "next";
import "../../app/globals.css";

export const metadata: Metadata = {
  title: "CIV 2026 Data Hackathon — what to expect",
  description: "From raw robotics recordings to reusable event logic and defensible proof.",
};

export default function PublicLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
