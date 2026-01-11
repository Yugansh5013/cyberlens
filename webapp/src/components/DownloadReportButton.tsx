"use client";

import { useState } from "react";
import { generateReport, openPdfBlob } from "@/lib/api";

export default function DownloadReportButton({ file_id }: { file_id: string }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const pdfBlob = await generateReport(file_id);
      openPdfBlob(pdfBlob, `SatyaSetu.AI_Report_${file_id}.pdf`);
    } catch (err) {
      console.error("❌ Failed to download report:", err);
      alert("Failed to generate report. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={downloading}
      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
    >
      {downloading ? "Generating..." : "⬇ Download Report"}
    </button>
  );
}
