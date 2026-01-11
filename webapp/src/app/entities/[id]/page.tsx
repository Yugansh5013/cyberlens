"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import RiskMeter from "@/components/RiskMeter";
import { useSatyaSetuAIStore } from "@/lib/store";
import { getEntityProfile, generateReport, openPdfBlob } from "@/lib/api";

export default function EntityProfilePage() {
  const params = useParams();
  // FIXED: Ensure 'id' is always a string, even if Next.js returns an array
  const id = Array.isArray(params.id) ? params.id[0] : params.id;

  const { setNotification, setLoading } = useSatyaSetuAIStore();

  const [profile, setProfile] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    async function fetchProfile() {
      if (!id) return;
      setLoading(true);
      setError(null);
      setNotification("Loading entity profile...");

      try {
        const decoded = decodeURIComponent(id);
        const res = await getEntityProfile(decoded);
        setProfile(res);
        setNotification("Entity loaded.");
      } catch (err: any) {
        if (err?.status === 404) {
          setError("No intelligence found for this entity.");
        } else {
          console.error(err);
          setError("Failed to fetch entity profile.");
        }
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, [id, setNotification, setLoading]); // Added dependencies for stability

  async function downloadReportForCase(file_id: string) {
    try {
      setDownloading(true);
      setNotification("Generating report...");
      const blob = await generateReport(file_id);
      openPdfBlob(blob, `${file_id}.pdf`);
      setNotification("Report ready for download.");
    } catch (e) {
      console.error(e);
      setNotification("Failed to generate report.");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-2">Entity Intelligence Profile</h1>
      <p className="text-gray-600 mb-6">
        Deep OSINT & case footprint for <b>{id ? decodeURIComponent(id) : ""}</b>
      </p>

      {error && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded mb-6">
          <strong>{error}</strong>
          <p className="text-sm text-gray-600 mt-2">
            Try re-analyzing evidence or check the analysis cache on the server.
          </p>
        </div>
      )}

      {profile && (
        <>
          <section className="bg-white shadow rounded-lg border p-6 mb-6">
            <h2 className="text-xl font-semibold mb-2">🚨 Risk Overview</h2>
            <RiskMeter score={(profile.avg_risk ?? 0) / 1} />
            <div className="mt-3 text-sm text-gray-700">
              <p><b>Found in:</b> {profile.found_in} case(s)</p>
              <p><b>Avg risk:</b> {Math.round((profile.avg_risk ?? 0) * 100) / 1}%</p>
              <p><b>Linked categories:</b> {profile.linked_categories?.join(", ") || "—"}</p>
            </div>
          </section>

          <section className="bg-white shadow rounded-lg border p-6 mb-6">
            <h2 className="text-xl font-semibold mb-3">🌐 OSINT Intelligence</h2>
            {/* Show a friendly list of OSINT hits from all cases */}
            <div className="space-y-3">
              {profile.cases?.map((c: any, idx: number) => (
                <div key={idx} className="p-3 border rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-sm text-cyan-600 font-medium">
                        Case: <a className="underline" href={`/cases/${c.case_id}`}>{c.case_id}</a>
                      </div>
                      <div className="text-sm text-gray-700">Category: {c.category || "Unknown"}</div>
                      <div className="text-sm text-gray-700">Risk score: {Math.round((c.risk_score ?? 0) * 100)}%</div>
                    </div>
                    <div>
                      <button
                        className="bg-cyan-600 text-white px-3 py-1 rounded hover:opacity-90"
                        onClick={() => downloadReportForCase(c.case_id)}
                        disabled={downloading}
                      >
                        {downloading ? "Preparing..." : "Download Report"}
                      </button>
                    </div>
                  </div>

                  {c.osint_hits && c.osint_hits.length > 0 && (
                    <div className="mt-2 text-xs text-gray-600">
                      OSINT hits: {JSON.stringify(c.osint_hits).slice(0, 200)}{c.osint_hits.length > 0 ? "..." : ""}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          <section className="bg-cyan-50 p-4 rounded border border-cyan-100">
            <h3 className="font-semibold mb-2">Intelligence Summary</h3>
            <ul className="list-disc list-inside text-sm text-gray-700">
              <li>Entities are cross-linked across all analyzed cases for reuse detection.</li>
              <li>Use the report button to download a full forensic PDF for any linked case.</li>
            </ul>
          </section>
        </>
      )}
    </main>
  );
}