import "@/styles/globals.css";
import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "CyberLens AI Forensics",
  description:
    "AI-powered cyber evidence analysis and OSINT intelligence platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen flex flex-col font-inter">
        {/* === Top Navigation === */}
        <nav className="bg-gray-900 text-white px-6 py-4 shadow-md flex justify-between items-center sticky top-0 z-50">
          {/* Brand */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-cyan-400 font-bold text-xl">CyberLens</span>
            <span className="hidden sm:inline text-sm text-gray-300">
              | AI Forensics Platform
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex gap-6 text-sm">
            <Link href="/upload" className="hover:text-cyan-300 transition">
              Upload Evidence
            </Link>
            <Link href="/dashboard" className="hover:text-cyan-300 transition">
              Dashboard
            </Link>
            <Link href="/batch" className="hover:text-cyan-600">Batch Analyzer</Link>
            <Link href="/report/unified" className="hover:text-cyan-300 transition">
              Unified Report
            </Link>
          </div>
        </nav>

        {/* === Page Content === */}
        <main className="flex-1 w-full px-4 sm:px-8 py-8">{children}</main>

        {/* === Footer === */}
        <footer className="bg-gray-900 text-gray-400 text-sm text-center py-4 mt-auto border-t border-gray-800">
          <p>
            CyberLens © {new Date().getFullYear()} — AI-Powered Digital
            Forensics Pipeline.
          </p>
        </footer>
      </body>
    </html>
  );
}
