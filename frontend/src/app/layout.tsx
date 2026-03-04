import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AlgoInfluencers - AI-Powered Influence Analytics",
  description: "Study how information spreads through social networks and predict viral content.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
