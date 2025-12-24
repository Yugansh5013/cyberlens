"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Shield, Upload, BarChart3, FileText } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-[calc(100vh-120px)] flex flex-col items-center justify-center text-center px-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="max-w-3xl mx-auto"
      >
        <div className="flex justify-center mb-4">
          <Shield className="w-14 h-14 text-cyan-500" />
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 text-gray-900">
          CyberLens <span className="text-cyan-600">AI Forensics</span>
        </h1>

        <p className="text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto mb-8">
          An AI-powered investigation toolkit that transforms digital evidence
          into actionable intelligence — combining OCR, NLP, Scam Classification,
          OSINT, and Risk Analytics in one seamless workflow.
        </p>

        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/upload"
            className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg font-medium shadow-md transition"
          >
            <div className="flex items-center gap-2 justify-center">
              <Upload className="w-4 h-4" /> Upload Evidence
            </div>
          </Link>

          <Link
            href="/dashboard"
            className="bg-gray-900 hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium shadow-md transition"
          >
            <div className="flex items-center gap-2 justify-center">
              <BarChart3 className="w-4 h-4" /> Dashboard
            </div>
          </Link>

          <Link
            href="/report/unified"
            className="bg-white border border-gray-300 hover:bg-gray-100 text-gray-800 px-6 py-3 rounded-lg font-medium shadow-md transition"
          >
            <div className="flex items-center gap-2 justify-center">
              <FileText className="w-4 h-4" /> Unified Report
            </div>
          </Link>
        </div>
      </motion.div>

      {/* Feature Grid */}
      <section className="mt-20 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 text-left hover:shadow-lg transition"
          >
            <div className="text-cyan-600 mb-3">{f.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{f.desc}</p>
          </motion.div>
        ))}
      </section>

      {/* Bottom Section */}
      <footer className="mt-20 text-gray-500 text-sm text-center">
        <p>Empowering investigators through automation, intelligence & clarity.</p>
        <p className="mt-2">
          Built with ❤️ using FastAPI, Next.js, and Machine Learning.
        </p>
      </footer>
    </main>
  );
}

// 🔍 Feature list for judges
const features = [
  {
    title: "OCR + NER Intelligence",
    desc: "Extract entities, URLs, and suspicious patterns from uploaded evidence using Optical Character Recognition and Named Entity Recognition.",
    icon: <Shield className="w-6 h-6" />,
  },
  {
    title: "Real-time Scam Classification",
    desc: "AI-powered text classifier detects potential fraud, phishing, and scam indicators across multiple case files in seconds.",
    icon: <BarChart3 className="w-6 h-6" />,
  },
  {
    title: "Heuristic + OSINT Risk Scoring",
    desc: "Integrates VirusTotal, OpenPhish, WHOIS, and heuristic checks to automatically assign cyber risk levels to domains and URLs.",
    icon: <FileText className="w-6 h-6" />,
  },
  {
    title: "Batch Intelligence Reports",
    desc: "Analyze multiple evidences simultaneously and generate unified reports that summarize patterns, risk clusters, and related entities.",
    icon: <Upload className="w-6 h-6" />,
  },
  {
    title: "Interactive Dashboard",
    desc: "Visualize clusters, top entities, and overall risk metrics to prioritize investigations efficiently.",
    icon: <BarChart3 className="w-6 h-6" />,
  },
  {
    title: "Automated Case Reports",
    desc: "Generate downloadable PDF reports for each case — reducing manual documentation time by up to 80%.",
    icon: <FileText className="w-6 h-6" />,
  },
];
