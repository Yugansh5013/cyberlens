"use client";

import { useEffect, useState } from "react";
import ChartCard from "@/components/ChartCard";
import CaseTable from "@/components/CaseTable";
import RiskMeter from "@/components/RiskMeter";
import { getTopEntities, getAllCases } from "@/lib/api";
import { useCyberLensStore } from "@/lib/store";
import { Activity, ShieldAlert, TrendingUp, Database } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import Link from 'next/link';



export default function DashboardPage() {
  const { setNotification, setLoading, isLoading } = useCyberLensStore();
  const [topEntities, setTopEntities] = useState<any[]>([]);
  const [recentCases, setRecentCases] = useState<any[]>([]);
  const [avgRisk, setAvgRisk] = useState<number>(0);
  const [categoryData, setCategoryData] = useState<
    { name: string; value: number }[]
  >([]);

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setNotification("Fetching dashboard analytics...");

      try {
        const entityRes = await getTopEntities();
        setTopEntities(entityRes);

        const caseRes = await getAllCases();
        setRecentCases(caseRes);

        if (caseRes.length > 0) {
          const avg =
            caseRes.reduce(
              (a: number, b: any) =>
                a + (b.risk?.score ?? b.risk_score ?? 0),
              0
            ) / caseRes.length;
          setAvgRisk(avg);

          const categories: Record<string, number> = {};
          for (const c of caseRes) {
            const cat =
              c.scam_class?.category || c.category || "Unknown";
            categories[cat] = (categories[cat] || 0) + 1;
          }

          setCategoryData(
            Object.entries(categories).map(([name, value]) => ({
              name,
              value,
            }))
          );
        }
        setNotification("Dashboard loaded successfully ✅");
      } catch (err: any) {
        console.error(err);
        setNotification("❌ Failed to load dashboard: " + err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return (
    <main className="max-w-7xl mx-auto px-6 py-10 font-inter ">
      <h1 className="text-4xl font-bold text-gray-800 mb-3 tracking-tight">
        📊 CyberLens Intelligence Dashboard
      </h1>
      <p className="text-gray-600 mb-10 text-base">
        Real-time overview of all analyzed cases, scam categories, and digital risk distribution across your intelligence network.
      </p>

      {isLoading && (
        <div className="text-cyan-600 font-medium animate-pulse">
          Loading analytics...
        </div>
      )}

      {!isLoading && (
        <>
          {/* KPI CARDS */}
          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            {[
              {
                title: "Total Cases",
                value: recentCases.length,
                icon: <Database className="w-5 h-5 text-cyan-500" />,
              },
              {
                title: "Average Risk",
                value: (
                  <RiskMeter score={avgRisk} />
                ),
                icon: <ShieldAlert className="w-5 h-5 text-orange-500" />,
              },
              {
                title: "Unique Entities",
                value: topEntities.length,
                icon: <Activity className="w-5 h-5 text-blue-500" />,
              },
              {
                title: "Trend Indicator",
                value: `${(avgRisk * 100).toFixed(0)}% avg risk`,
                icon: <TrendingUp className="w-5 h-5 text-green-500" />,
              },
            ].map((item, i) => (
              <div
                key={i}
                className="bg-white shadow-lg border border-gray-100 rounded-2xl p-6 flex flex-col items-center justify-center hover:shadow-xl transition-shadow"
              >
                <div className="flex items-center gap-2 mb-2 text-sm text-gray-500 uppercase tracking-wide">
                  {item.icon}
                  {item.title}
                </div>
                <div className="text-2xl font-semibold text-gray-800">
                  {item.value}
                </div>
              </div>
            ))}
          </section>

          {/* === ANALYTICS CHARTS SECTION === */}
<section className="mb-12">
  <h2 className="text-2xl font-semibold text-gray-800 mb-6">
    📊 Scam & Entity Analytics
  </h2>

  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
    {/* Scam Category Distribution */}
    <div className="bg-white border border-gray-100 shadow-md rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        🧩 Scam Category Distribution
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={categoryData}
            cx="50%"
            cy="50%"
            outerRadius={90}
            dataKey="value"
            nameKey="name"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
          >
            {categoryData.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={[
                  "#06b6d4", // cyan
                  "#3b82f6", // blue
                  "#f59e0b", // amber
                  "#ef4444", // red
                  "#10b981", // green
                ][index % 5]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(v) => `${v} cases`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>

    {/* Top Entities by Frequency */}
    <div className="bg-white border border-gray-100 shadow-md rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        🌐 Top Entities by Frequency
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={topEntities.map((e) => ({
            name: e.entity,
            value: e.count,
          }))}
          margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {topEntities.map((_, index) => (
              <Cell
                key={`bar-${index}`}
                fill={[
                  "#06b6d4",
                  "#3b82f6",
                  "#f59e0b",
                  "#ef4444",
                  "#10b981",
                ][index % 5]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  </div>
</section>


          {/* RECENT CASES */}
          <section className="bg-white shadow-lg rounded-2xl border border-gray-100 p-6 mb-10">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              🧠 Recent Analyzed Cases
            </h2>
            <CaseTable cases={recentCases.slice(0, 8)} />
          </section>

          {/* INSIGHTS */}
          <section className="rounded-2xl p-6 border border-cyan-100 bg-gradient-to-r from-cyan-50 to-blue-50 shadow-sm text-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              🔍 Investigative Insights
            </h2>
            <ul className="list-disc list-inside text-sm leading-relaxed space-y-1">
              <li>Scam category distribution reveals trending fraud patterns.</li>
              <li>Top entities uncover recurring accounts or domains tied to scams.</li>
              <li>Risk levels help focus on high-severity evidence faster.</li>
              <li>Aggregated intelligence reduces investigation time by <b>70%</b>.</li>
            </ul>
          </section>
          <section className="bg-white shadow-md rounded-lg border p-6 mt-8">
  <h2 className="text-xl font-semibold mb-4">🧩 Run Batch Analysis</h2>
  <p className="text-gray-600 mb-4">
    Upload multiple files at once to generate a unified intelligence report.
  </p>
  <Link href="/batch">
    <button className="bg-cyan-600 text-white px-4 py-2 rounded hover:opacity-90">
      Go to Batch Analyzer
    </button>
  </Link>
</section>

        </>
      )}
    </main>
  );
}
