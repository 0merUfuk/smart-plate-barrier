import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Akıllı Plaka Tanıma ve Bariyer Sistemi",
  description: "Akıllı Plaka Tanıma ve Bariyer Sistemi frontend geliştirme ortamı.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
