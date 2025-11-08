export default function RiskMeter({ score }: { score: number }) {
  const color =
    score >= 0.75 ? "bg-red-500" : score >= 0.45 ? "bg-yellow-400" : "bg-green-500";
  const label =
    score >= 0.75 ? "HIGH" : score >= 0.45 ? "MEDIUM" : "LOW";

  return (
    <div className="space-y-1">
      <div className="text-sm font-medium">Risk Level: {label}</div>
      <div className="w-full h-3 bg-gray-200 rounded">
        <div className={`h-3 ${color} rounded`} style={{ width: `${score * 100}%` }} />
      </div>
    </div>
  );
}
