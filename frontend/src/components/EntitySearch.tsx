"use client";
export default function EntitySearch({
  query,
  setQuery,
  onSearch,
  loading,
}: {
  query: string;
  setQuery: (v: string) => void;
  onSearch: () => void;
  loading: boolean;
}) {
  return (
    <div className="flex gap-3">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search emails, URLs, UPI, or phone..."
        className="border border-gray-300 rounded px-4 py-2 flex-1"
      />
      <button
        onClick={onSearch}
        disabled={loading}
        className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-800"
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </div>
  );
}
