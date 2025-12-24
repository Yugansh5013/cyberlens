"use client";

import Link from "next/link";

export default function CaseTable({ cases }: { cases: any[] }) {
  if (!cases || cases.length === 0)
    return <p className="text-gray-500 text-sm">No cases found.</p>;

  return (
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="bg-gray-100 border-b">
          <th className="p-2 text-left">File ID</th>
          <th className="p-2 text-left">Category</th>
          <th className="p-2 text-left">Risk</th>
          <th className="p-2 text-left">Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {cases.map((c) => (
          <tr key={c.file_id} className="border-b hover:bg-gray-50">
            <td className="p-2">
              <Link href={`/cases/${c.file_id}`} className="text-cyan-600 hover:underline">
                {c.file_id}
              </Link>
            </td>
            <td className="p-2">{c.scam_class?.category || "Unknown"}</td>
            <td className="p-2">{Math.round((c.risk?.score ?? 0) * 100)}%</td>
            <td className="p-2">{c.analyzed_at}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
