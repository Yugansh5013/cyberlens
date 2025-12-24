"use client";

export default function RiskMeter({ score }: { score: number }) {
  const percent = Math.round(score * 100);
  const color =
    percent >= 75
      ? "bg-red-600"
      : percent >= 45
      ? "bg-orange-500"
      : "bg-green-500";

  return (
    <div className="my-2">
      <div className="w-full bg-gray-200 h-4 rounded-full overflow-hidden">
        <div className={`${color} h-4`} style={{ width: `${percent}%` }} />
      </div>
      <p className="text-sm text-gray-600 mt-1 font-medium">
        Risk Score: {percent}%
      </p>
    </div>
  );
}
