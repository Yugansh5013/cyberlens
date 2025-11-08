"use client";
import Link from "next/link";

export default function Home() {
  return (
    <div className="text-center py-20">
      <h1 className="text-5xl font-bold text-blue-900 mb-6">CyberLens</h1>
      <p className="text-lg text-gray-700 mb-10">
        AI-Powered Scam Forensics — bridging citizens, OSINT, and law enforcement.
      </p>
      <Link
        href="/upload"
        className="bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-800 transition"
      >
        Start Investigation →
      </Link>
    </div>
  );
}
