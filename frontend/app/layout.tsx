import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Korfbal Live Analytics',
  description: 'Heatmaps en shotstatistieken voor korfbalwedstrijden',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl">
      <body className="bg-slate-950 text-slate-100 min-h-screen">{children}</body>
    </html>
  );
}
