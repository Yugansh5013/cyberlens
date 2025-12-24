import Link from "next/link";

export default function EntityCard({
  type,
  value,
  riskLevel,
  clickable = false,
}: {
  type: string;
  value: string;
  riskLevel?: string;
  clickable?: boolean;
}) {
  return (
    <div className="border rounded-lg p-3 bg-green-50 hover:bg-green-100 transition">
      <p className="text-xs text-green-600 font-semibold">{type}</p>
      {clickable ? (
        <Link
          href={`/entities/${encodeURIComponent(value)}`}
          className="text-blue-600 hover:underline text-sm"
        >
          {value}
        </Link>
      ) : (
        <p className="text-sm text-gray-800">{value}</p>
      )}
    </div>
  );
}
