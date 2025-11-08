export default function ThreatCard({ threat }: { threat: any }) {
  return (
    <div className="bg-white p-4 rounded shadow-sm border border-gray-100 hover:shadow-md transition">
      <div className="font-semibold text-blue-700">{threat.value}</div>
      <div className="text-sm text-gray-600">Type: {threat.type}</div>
      <div className="text-xs text-gray-500 mt-1">
        Last seen: {threat.last_seen || "N/A"} | Risk: {(threat.risk_score * 100).toFixed(1)}%
      </div>
    </div>
  );
}
