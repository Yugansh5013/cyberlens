"use client";
import { useState, useEffect } from "react";
import { searchEntities, getTopEntities } from "@/lib/api";
import ThreatCard from "@/components/ThreatCard";
import EntitySearch from "@/components/EntitySearch";

export default function ThreatHub() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [top, setTop] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getTopEntities().then(setTop);
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const data = await searchEntities(query);
    setResults(data.results || []);
    setLoading(false);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Threat Intelligence Hub</h1>

      <EntitySearch
        query={query}
        setQuery={setQuery}
        onSearch={handleSearch}
        loading={loading}
      />

      {results.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-lg">Search Results</h2>
          {results.map((r, i) => (
            <ThreatCard key={i} threat={r} />
          ))}
        </div>
      )}

      <div className="mt-10">
        <h2 className="font-semibold text-lg mb-3">Top Reported Entities</h2>
        <div className="grid grid-cols-3 gap-4">
          {top.map((t, i) => (
            <div key={i} className="bg-white p-3 rounded shadow text-sm">
              <div className="font-semibold">{t.entity}</div>
              <div className="text-gray-600">{t.count} occurrences</div>
              <div className="text-xs text-blue-700">{t.type}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
