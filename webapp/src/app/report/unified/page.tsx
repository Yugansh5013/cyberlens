"use client";

import React, { useState } from "react";
import axios from "axios";

/**
 * Unified Report Page
 * - Input: batch_id
 * - POST /api/unified-report (form field: batch_id)
 * - Displays a concise dashboard: total_cases, avg risk, dominant category, top entities
 * - Allows downloading the returned JSON as a file
 */

type UnifiedSummary = {
  batch_id: string;
  summary?: {
    total_cases?: number;
    unique_entities?: number;
    average_risk?: number;
    dominant_category?: string;
    categories?: Record<string, number>;
    entities_sample?: string[];
  };
  cases?: any[];
};

export default function UnifiedReportPage() {
  const [batchId, setBatchId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UnifiedSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api";

  const fetchUnifiedReport = async (e?: React.FormEvent) => {
  e?.preventDefault();
  setError(null);
  setResult(null);

  if (!batchId) {
    setError("Please enter a batch id (example: 1a2b3c4d).");
    return;
  }

  setLoading(true);
  try {
    const form = new FormData();
    form.append("batch_id", batchId);

    const resp = await axios.post(`${apiBase}/unified-report`, form, {
      responseType: "json",
    });

    setResult(resp.data);
  } catch (err: any) {
    console.error("❌ Unified Report Error:", err.response?.data || err);
    setError(
      typeof err?.response?.data?.detail === "string"
        ? err.response.data.detail
        : JSON.stringify(err.response?.data?.detail, null, 2)
    );
  } finally {
    setLoading(false);
  }
};


  const downloadJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `unified_report_${result.batch_id || "report"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-3">Unified Batch Report</h1>
      <p className="text-sm text-gray-600 mb-6">
        Generate and preview a unified intelligence summary for a processed batch. Paste the <code>batch_id</code> you received after running batch analysis.
      </p>

      <form onSubmit={fetchUnifiedReport} className="flex gap-2 mb-4">
        <input
          value={batchId}
          onChange={(ev) => setBatchId(ev.target.value.trim())}
          placeholder="Enter batch id (e.g. ab12cd34)"
          className="flex-1 border px-3 py-2 rounded"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
        <button
          type="button"
          onClick={() => {
            setBatchId("");
            setResult(null);
            setError(null);
          }}
          className="ml-2 px-3 py-2 border rounded"
        >
          Reset
        </button>
      </form>

      {error && <div className="text-red-600 mb-4">{error}</div>}

      {!result && !error && (
        <div className="text-sm text-gray-500 mb-6">
          Tip: run the batch analyzer (`/api/batch-analyze`) to produce a batch_id, or check the backend cache folder `app/data/analysis_cache` for `batch_&lt;id&gt;.json`.
        </div>
      )}

      {result && (
        <section className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white border rounded shadow-sm">
              <div className="text-sm text-gray-500">Batch ID</div>
              <div className="font-mono mt-1">{result.batch_id}</div>
            </div>

            <div className="p-4 bg-white border rounded shadow-sm">
              <div className="text-sm text-gray-500">Total Cases</div>
              <div className="text-2xl font-bold mt-1">
                {result.summary?.total_cases ?? "—"}
              </div>
            </div>

            <div className="p-4 bg-white border rounded shadow-sm">
              <div className="text-sm text-gray-500">Average Risk</div>
              <div className="text-2xl font-bold mt-1">
                {(result.summary?.average_risk ?? 0).toFixed(2)}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white border rounded shadow-sm">
              <h3 className="font-semibold mb-2">Dominant Category</h3>
              <div className="text-lg">{result.summary?.dominant_category ?? "Unknown"}</div>

              <h4 className="mt-4 font-medium">Category Breakdown</h4>
              <ul className="mt-2 text-sm space-y-1">
                {result.summary?.categories
                  ? Object.entries(result.summary.categories).map(([k, v]) => (
                      <li key={k}>
                        <b>{k}</b>: {v}
                      </li>
                    ))
                  : <li className="text-gray-500">No category data</li>}
              </ul>
            </div>

            <div className="p-4 bg-white border rounded shadow-sm">
              <h3 className="font-semibold mb-2">Entities (sample)</h3>
              <div className="text-sm text-gray-700">
                {result.summary?.entities_sample?.length ? (
                  <ol className="list-decimal pl-5 space-y-1">
                    {result.summary.entities_sample.map((e, i) => (
                      <li key={i} className="truncate">{e}</li>
                    ))}
                  </ol>
                ) : (
                  <div className="text-gray-500">No entity sample available</div>
                )}
              </div>
            </div>
          </div>

          {/* Cases preview */}
          <div className="bg-white border rounded shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">Cases (preview)</h3>
              <div className="flex gap-2">
                <button onClick={downloadJSON} className="px-3 py-1 border rounded text-sm">
                  ⤓ Download JSON
                </button>
                <button
                  onClick={() => {
                    // quick export to clipboard
                    navigator.clipboard?.writeText(JSON.stringify(result, null, 2));
                    alert("Copied JSON summary to clipboard");
                  }}
                  className="px-3 py-1 border rounded text-sm"
                >
                  Copy JSON
                </button>
              </div>
            </div>

            {result.cases?.length ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm table-auto">
                  <thead className="text-left bg-gray-50">
                    <tr>
                      <th className="p-2">Case ID</th>
                      <th className="p-2">Category</th>
                      <th className="p-2">Risk</th>
                      <th className="p-2">Entities</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.cases.slice(0, 15).map((c: any) => (
                      <tr key={c.file_id} className="border-t">
                        <td className="p-2 font-mono text-xs">{c.file_id}</td>
                        <td className="p-2">{c.scam_class?.category ?? "—"}</td>
                        <td className="p-2">{c.risk?.score ?? "—"}</td>
                        <td className="p-2 max-w-xl truncate">{(c.entities || []).map((e:any)=>e.value || e).slice(0,6).join(", ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-gray-500">No cases returned in this batch.</div>
            )}
          </div>
        </section>
      )}
    </main>
  );
}
