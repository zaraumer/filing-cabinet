import type { Metadata } from "next";
import { DM_Sans, DM_Serif_Display, Geist_Mono } from "next/font/google";
import "./globals.css";

import SiteHeader from "@/components/SiteHeader";

// DM Sans carries all functional UI: navigation, body copy, tables, inputs.
const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
});

// DM Serif Display is used sparingly: the wordmark and major page headings.
const dmSerifDisplay = DM_Serif_Display({
  variable: "--font-dm-serif-display",
  weight: "400",
  subsets: ["latin"],
});

// Reserved for reference numbers and other identifiers.
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Filing Cabinet",
  description: "Records digitization, search, and verification platform",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${dmSans.variable} ${dmSerifDisplay.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-page font-sans text-ink">
        <SiteHeader />
        <div className="flex-1">{children}</div>
      </body>
    </html>
  );
}
