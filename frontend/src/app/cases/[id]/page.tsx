"use client";
import { useEffect, useState } from "react";
import { analyzeEvidence, generateReport } from "@/lib/api";
import RiskMeter from "@/components/RiskMeter";

export default function CasePage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyzeEvidence(params.id).then((res) => {
      setData(res);
      setLoading(false);
    });
  }, [params.id]);

  const handleDownload = async () => {
    const blob = await generateReport(params.id);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cyberlens_${params.id}.pdf`;
    a.click();
  };

  if (loading) return <p>Analyzing evidence...</p>;
  if (!data) return <p>No data found.</p>;

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Case Analysis</h1>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Scam Classification</h2>
        <p><b>Category:</b> {data.scam_class?.category}</p>
        <p><b>Confidence:</b> {(data.scam_class?.confidence * 100).toFixed(1)}%</p>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Risk Assessment</h2>
        <RiskMeter score={data.risk?.score || 0} />
        <p className="mt-2 text-sm text-gray-700">{data.risk?.rationale}</p>
      </div>

      <button
        onClick={handleDownload}
        className="bg-green-600 text-white px-5 py-2 rounded"
      >
        Download PDF Report
      </button>
    </div>
  );
}
