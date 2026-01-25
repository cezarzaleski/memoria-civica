import type { Metadata, Viewport } from 'next';
import './globals.css';
import { MSWInitializer } from './msw-initializer';

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  minimumScale: 1,
  maximumScale: 5,
  userScalable: true,
  viewportFit: 'cover',
};

export const metadata: Metadata = {
  title: 'Memória Cívica',
  description: 'Acompanhe votações e deputados do Congresso Nacional',
  generator: 'next.js',
  applicationName: 'Memória Cívica',
  keywords: ['votações', 'deputados', 'congresso', 'câmara', 'deputados federais'],
  manifest: '/manifest.webmanifest',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    minimumScale: 1,
    maximumScale: 5,
    userScalable: true,
    viewportFit: 'cover',
  },
  icons: {
    icon: [
      {
        url: '/favicon.ico',
        type: 'image/x-icon',
      },
      {
        url: '/icons/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        url: '/icons/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
    apple: [
      {
        url: '/icons/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        url: '/icons/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  },
  themeColor: '#1d4ed8',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Memória Cívica',
    startupImage: '/icons/icon-512.png',
  },
  formatDetection: {
    telephone: false,
    email: true,
    address: false,
  },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: process.env.NEXT_PUBLIC_SITE_URL || 'https://memoria-civica.com',
    siteName: 'Memória Cívica',
    title: 'Memória Cívica',
    description: 'Acompanhe votações e deputados do Congresso Nacional',
    images: [
      {
        url: '/icons/icon-512.png',
        width: 512,
        height: 512,
        alt: 'Memória Cívica Logo',
        type: 'image/png',
      },
    ],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <MSWInitializer />
        <div className="relative flex h-screen flex-col">
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}
