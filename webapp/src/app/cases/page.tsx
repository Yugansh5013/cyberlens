"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { searchCases } from "@/lib/api";
import { Search, FileText, AlertCircle, CheckCircle, Clock } from "lucide-react";

interface CaseItem {
  file_id: string;
  scam_class: {
    category: string;
  };
  risk: {
    score: number;
    risk_level: string;
  };
  analyzed_at: string;
}

export default function CasesPage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredCases, setFilteredCases] = useState<CaseItem[]>([]);

  useEffect(() => {
    loadCases();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredCases(cases);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredCases(
        cases.filter(
          (c) =>
            c.file_id.toLowerCase().includes(query) ||
            c.scam_class?.category?.toLowerCase().includes(query) ||
            c.risk?.risk_level?.toLowerCase().includes(query)
        )
      );
    }
  }, [searchQuery, cases]);

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await searchCases("");
      if (Array.isArray(data)) {
        setCases(data);
        setFilteredCases(data);
      } else {
        setCases([]);
        setFilteredCases([]);
      }
    } catch (error) {
      console.error("Failed to load cases:", error);
      setCases([]);
      setFilteredCases([]);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200";
      case "medium":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "low":
        return "text-green-600 bg-green-50 border-green-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case "medium":
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case "low":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      default:
        return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-cyan-50 py-12 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📂 All Analyzed Cases
          </h1>
          <p className="text-gray-600">
            Browse and search through all analyzed evidence files
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by file ID, category, or risk level..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
        </motion.div>

        {/* Stats Overview */}
        {!loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
          >
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <p className="text-sm text-gray-600">Total Cases</p>
              <p className="text-3xl font-bold text-gray-900">{cases.length}</p>
            </div>
            <div className="bg-red-50 rounded-lg shadow p-4 text-center">
              <p className="text-sm text-gray-600">High Risk</p>
              <p className="text-3xl font-bold text-red-600">
                {cases.filter((c) => c.risk?.risk_level?.toLowerCase() === "high").length}
              </p>
            </div>
            <div className="bg-yellow-50 rounded-lg shadow p-4 text-center">
              <p className="text-sm text-gray-600">Medium Risk</p>
              <p className="text-3xl font-bold text-yellow-600">
                {cases.filter((c) => c.risk?.risk_level?.toLowerCase() === "medium").length}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-4 text-center">
              <p className="text-sm text-gray-600">Low Risk</p>
              <p className="text-3xl font-bold text-green-600">
                {cases.filter((c) => c.risk?.risk_level?.toLowerCase() === "low").length}
              </p>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading cases...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredCases.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12 bg-white rounded-lg shadow"
          >
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No cases found
            </h3>
            <p className="text-gray-500 mb-6">
              {searchQuery
                ? "Try adjusting your search query"
                : "Upload and analyze evidence to see cases here"}
            </p>
            <Link
              href="/upload"
              className="inline-block bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg font-medium transition"
            >
              Upload Evidence
            </Link>
          </motion.div>
        )}

        {/* Cases Grid */}
        {!loading && filteredCases.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {filteredCases.map((caseItem, idx) => (
              <motion.div
                key={caseItem.file_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Link href={`/cases/${caseItem.file_id}`}>
                  <div className="bg-white rounded-lg shadow hover:shadow-lg transition border border-gray-200 p-5 cursor-pointer">
                    {/* Risk Badge */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        {getRiskIcon(caseItem.risk?.risk_level)}
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRiskColor(
                            caseItem.risk?.risk_level
                          )}`}
                        >
                          {caseItem.risk?.risk_level?.toUpperCase() || "N/A"}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        Score: {caseItem.risk?.score?.toFixed(2) || "N/A"}
                      </span>
                    </div>

                    {/* File ID */}
                    <h3 className="font-semibold text-gray-900 mb-2 truncate">
                      {caseItem.file_id}
                    </h3>

                    {/* Category */}
                    <p className="text-sm text-gray-600 mb-3">
                      <span className="font-medium">Category:</span>{" "}
                      {caseItem.scam_class?.category || "Unknown"}
                    </p>

                    {/* Timestamp */}
                    <p className="text-xs text-gray-500">
                      Analyzed: {caseItem.analyzed_at || "N/A"}
                    </p>
                  </div>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </main>
  );
}
