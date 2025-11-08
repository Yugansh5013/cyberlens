import "../styles/globals.css";
import Link from "next/link";

export const metadata = {
  title: "CyberLens",
  description: "AI-powered scam forensic platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="bg-blue-900 text-white py-4 shadow">
          <div className="max-w-6xl mx-auto flex justify-between items-center px-6">
            <Link href="/" className="text-2xl font-bold">CyberLens</Link>
            <nav className="space-x-6">
              <Link href="/upload" className="hover:underline">Upload</Link>
              <Link href="/cases/demo" className="hover:underline">Cases</Link>
              <Link href="/report/demo" className="hover:underline">Reports</Link>
              <Link href="/hub" className="hover:underline">Threat Hub</Link>
<Link href="/report/unified" className="hover:underline">Unified Report</Link>

            </nav>
          </div>
        </header>

        <main className="max-w-6xl mx-auto py-10 px-4">
          {children}
        </main>
      </body>
    </html>
  );
}
