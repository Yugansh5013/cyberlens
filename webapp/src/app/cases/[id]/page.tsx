"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import RiskMeter from "@/components/RiskMeter";
import EntityCard from "@/components/EntityCard";
import { useCyberLensStore } from "@/lib/store";
import {
  getCaseFromCache,
  analyzeEvidence,
  generateReport,
  openPdfBlob,
} from "@/lib/api";
import DownloadReportButton from "@/components/DownloadReportButton";

export default function CaseAnalysisPage() {
  const { id } = useParams();
  const { getCaseData, setAnalysis, setNotification, setLoading, isLoading } =
    useCyberLensStore();

  const [caseData, setCaseData] = useState<any | null>(null);

  // 🧠 Load from cache or backend
  useEffect(() => {
    async function loadCase() {
      if (!id) return;
      setLoading(true);

      try {
        // Try cache first (Zustand)
        const cached = getCaseData(id as string);
        if (cached) {
          setCaseData(cached);
          setNotification("Loaded case from cache ✅");
          setLoading(false);
          return;
        }

        // Otherwise fetch from backend
        setNotification("Fetching case details from server...");
        const res = await getCaseFromCache(id as string);

        if (!res || !res.file_id) {
          // If not in cache, re-analyze
          setNotification("Re-analyzing case...");
          const fresh = await analyzeEvidence(id as string);
          setAnalysis(id as string, fresh);
          setCaseData(fresh);
        } else {
          setAnalysis(id as string, res);
          setCaseData(res);
        }
        setNotification("Case loaded successfully ✅");
      } catch (err: any) {
        console.error(err);
        setNotification("❌ Failed to load case: " + err.message);
      } finally {
        setLoading(false);
      }
    }
    loadCase();
  }, [id]);

  if (isLoading) {
    return (
      <div className="text-center text-cyan-600 font-medium mt-20 animate-pulse">
        Loading case details... 🔍
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="text-center text-gray-600 mt-20">
        No data found for this case.
      </div>
    );
  }

  const { scam_class, risk, entities, osint_hits, url_qr_findings } = caseData;

  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-10">
      {/* HEADER */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">
            Case Intelligence: {caseData.file_id}
          </h1>
          <p className="text-sm text-gray-500">
            Analyzed at {caseData.analyzed_at}
          </p>
        </div>
        <button
  onClick={async () => {
    try {
      setLoading(true);
      const blob = await generateReport(caseData.file_id);
      openPdfBlob(blob, `${caseData.file_id}.pdf`);
      setNotification("Report downloaded ✅");
    } catch (e: any) {
      console.error(e);
      setNotification("❌ Failed to download report: " + e.message);
    } finally {
      setLoading(false);
    }
  }}
  className="px-4 py-2 bg-cyan-600 text-white rounded shadow"
>
  Download PDF report
</button>
      </div>

      {/* SCAM CLASSIFICATION */}
      <section className="bg-white shadow rounded-lg border p-6 mb-8">
        <h2 className="text-xl font-semibold mb-2">🧩 Scam Classification</h2>
        <p>
          <b>Category:</b> {scam_class?.category || "Unknown"}
        </p>
        <p>
          <b>Confidence:</b>{" "}
          {Math.round((scam_class?.confidence ?? 0) * 100)}%
        </p>
        {scam_class?.keywords?.length > 0 && (
          <p>
            <b>Keywords:</b> {scam_class.keywords.join(", ")}
          </p>
        )}
      </section>

      {/* RISK ANALYSIS */}
      <section className="bg-white shadow rounded-lg border p-6 mb-8">
        <h2 className="text-xl font-semibold mb-3">🚨 Risk Analysis</h2>
        <RiskMeter score={risk?.score ?? 0} />
        <p className="text-sm mt-2 text-gray-700">
          <b>Level:</b> {risk?.risk_level}
        </p>
        <p className="text-sm text-gray-600 mt-1">
          <b>Rationale:</b> {risk?.rationale}
        </p>

        {risk?.factors && (
          <div className="mt-3 text-xs bg-gray-50 p-3 rounded border">
            <p>
              <b>Factors:</b>
            </p>
            <ul className="list-disc list-inside text-gray-700">
              <li>Scam Confidence: {risk.factors.scam_confidence}</li>
              <li>Avg Entity Risk: {risk.factors.avg_entity_risk}</li>
              <li>Keyword Toxicity: {risk.factors.keyword_toxicity}</li>
              <li>
                Sentiment Uncertainty: {risk.factors.sentiment_uncertainty}
              </li>
              <li>OSINT Weight: {risk.factors.osint_weight}</li>
            </ul>
          </div>
        )}
      </section>

      {/* ENTITIES */}
      {entities?.length > 0 && (
        <section className="bg-white shadow rounded-lg border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">🧾 Extracted Entities</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {entities.map((e: any, i: number) => (
              <EntityCard
                key={i}
                type={e.type}
                value={e.value}
                riskLevel={e.risk_level}
                clickable
              />
            ))}
          </div>
        </section>
      )}

      {/* OSINT RESULTS */}
      {osint_hits?.length > 0 && (
        <section className="bg-white shadow rounded-lg border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">
            🌐 OSINT Intelligence Findings
          </h2>
          <ul className="text-sm list-disc list-inside space-y-1 text-gray-700">
            {osint_hits.map((o: any, i: number) => (
              <li key={i}>
                {typeof o === "string"
                  ? o
                  : JSON.stringify(o, null, 2).slice(0, 200)}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* URL/QR */}
      {url_qr_findings?.length > 0 && (
        <section className="bg-white shadow rounded-lg border p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">
            🔗 URL & QR Code Intelligence
          </h2>
          <ul className="text-sm list-disc list-inside text-gray-700 space-y-1">
            {url_qr_findings.map((u: any, i: number) => (
              <li key={i}>
                <a
                  href={u.url}
                  target="_blank"
                  className="text-cyan-600 hover:underline"
                >
                  {u.url}
                </a>{" "}
                — Risk: <b>{u.risk_level}</b> ({u.combined_risk}%)
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
