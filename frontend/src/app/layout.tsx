import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Bowen - NZ Legal Information Assistant',
  description: 'AI-powered legal information tool for New Zealand legislation. Get instant answers with citations to official sources.',
  keywords: ['New Zealand law', 'legal information', 'NZ legislation', 'legal assistant'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="stylesheet" href="https://use.typekit.net/czn0xnx.css" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
