import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Memória Cívica',
  description: 'Acompanhe votações e deputados do Congresso Nacional',
  generator: 'next.js',
  applicationName: 'Memória Cívica',
  keywords: ['votações', 'deputados', 'congresso'],
  icons: {
    icon: '/favicon.ico',
  },
  themeColor: '#1d4ed8',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <div className="relative flex h-screen flex-col">
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}
