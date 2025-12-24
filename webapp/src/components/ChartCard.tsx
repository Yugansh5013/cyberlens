"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

export default function ChartCard({
  data,
  title,
}: {
  data: { name: string; value: number }[];
  title: string;
}) {
  const COLORS = ["#00bcd4", "#f59e0b", "#ef4444", "#10b981", "#6366f1"];

  return (
    <div className="bg-white shadow rounded-lg p-4 w-full md:w-1/2">
      <h3 className="font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
