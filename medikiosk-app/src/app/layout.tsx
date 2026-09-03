import type { Metadata, Viewport } from 'next';
import { Inter, Noto_Sans } from 'next/font/google';
import './globals.css';
import EmergencyOverlay from '@/components/modals/EmergencyOverlay';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const notoSans = Noto_Sans({
  subsets: ['latin', 'devanagari'],
  variable: '--font-noto-sans',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'MediKiosk — AI Clinical History & Intake Platform',
  description:
    'Multimodal conversational clinical intake, document digitization, and ABDM/FHIR interoperability kiosk for Indian hospitals.',
  keywords: [
    'MediKiosk',
    'Clinical Intake',
    'ABHA',
    'ABDM',
    'FHIR',
    'AYUSH',
    'Hospital Kiosk',
  ],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${notoSans.variable} h-full w-full antialiased`}
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="h-screen w-screen overflow-hidden bg-[#f8fafa] text-[#191c1d] flex flex-col font-sans select-none">
        {children}
        <EmergencyOverlay />
      </body>
    </html>
  );
}
