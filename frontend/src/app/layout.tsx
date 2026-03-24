import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wire Color Classifier",
  description: "Industrial wire color detection & analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
