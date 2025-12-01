import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PriceHistoryPoint } from "../api/client";

interface Props {
  data: PriceHistoryPoint[];
}

function PriceChart({ data }: Props) {
  if (!data || data.length === 0) {
    return <div className="muted">Not enough history yet.</div>;
  }

  return (
    <div style={{ width: "100%", height: 240 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="date" tick={{ fill: "#cbd5e1" }} />
          <YAxis tick={{ fill: "#cbd5e1" }} width={60} />
          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #1f2937" }}
            labelStyle={{ color: "#e2e8f0" }}
          />
          <Line type="monotone" dataKey="min_price" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceChart;
