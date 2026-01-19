import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Travel Planner India - Multi-Modal Journey Planner",
  description: "Plan your journey across India with flights, trains, and buses. Find the best routes, prices, and schedules.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-gradient-to-br from-gray-50 to-saffron-50/30">
        {children}
      </body>
    </html>
  );
}
