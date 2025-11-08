export default function StatCard({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="bg-white rounded shadow p-4 text-center">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-bold text-blue-800 mt-1">{value}</div>
    </div>
  );
}
