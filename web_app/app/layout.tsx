import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Winsanity - AI-Powered Stock Analysis & Market Insights",
  description: "Advanced stock analysis platform powered by AI. Get real-time market data, AI-driven predictions, analyst ratings comparison, earnings transcripts analysis, and comprehensive stock reports all in one dashboard.",
  keywords: [
    "stock analysis",
    "AI stock predictions",
    "stock market analysis",
    "analyst ratings",
    "earnings transcripts",
    "stock comparison",
    "market insights",
    "trading platform",
    "financial analysis",
    "AI investing",
    "Winsanity"
  ],
  authors: [{ name: "Winsanity" }],
  creator: "Winsanity",
  publisher: "Winsanity",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  // openGraph: {
  //   type: "website",
  //   locale: "en_US",
  //   url: "https://winsanity.com", // Update with your actual domain
  //   title: "Winsanity - AI-Powered Stock Analysis & Market Insights",
  //   description: "Advanced stock analysis platform powered by AI. Get real-time market data, AI-driven predictions, analyst ratings comparison, and comprehensive stock reports.",
  //   siteName: "Winsanity",
  //   images: [
  //     {
  //       url: "/og-image.png", // Create this image (1200x630px recommended)
  //       width: 1200,
  //       height: 630,
  //       alt: "Winsanity Dashboard Preview",
  //     },
  //   ],
  // },
  // twitter: {
  //   card: "summary_large_image",
  //   title: "Winsanity - AI-Powered Stock Analysis & Market Insights",
  //   description: "Advanced stock analysis platform powered by AI. Get real-time market data, AI-driven predictions, and comprehensive stock reports.",
  //   images: ["/twitter-image.png"], // Create this image (1200x600px recommended)
  //   creator: "@winsanity", // Update with your Twitter handle
  // },
  // viewport: {
  //   width: "device-width",
  //   initialScale: 1,
  //   maximumScale: 1,
  // },
  // verification: {
  //   // google: "your-google-verification-code", // Add when you set up Google Search Console
  // },
  category: "finance",
  applicationName: "Winsanity",
  // appleWebApp: {
  //   capable: true,
  //   title: "Winsanity",
  //   statusBarStyle: "black-translucent",
  // },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
