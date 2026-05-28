import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';
import { ForecastHistoryItem } from '../api/client';

interface HistoryChartProps {
  history: ForecastHistoryItem[];
  stationName: string;
}

export default function HistoryChart({ history, stationName }: HistoryChartProps) {
  if (!history || history.length === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', color: '#94a3b8' }}>
        No history data available for {stationName}
      </div>
    );
  }

  const chartData = history.map((item, i) => ({
    time: item.timestamp,
    q10: item.q10,
    q25: item.q25,
    q50: item.q50,
    q75: item.q75,
    q90: item.q90,
    actual: item.actual_water_level,
  }));

  return (
    <div>
      <h3 style={{ margin: '24px 0 8px', color: '#1e293b' }}>
        {stationName} — Last 30 Days Forecast vs Actuals
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <XAxis
            dataKey="time"
            tickFormatter={(val: any) => new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
            minTickGap={50}
          />
          <YAxis label={{ value: 'Water Level (m)', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            labelFormatter={(label: any) => new Date(label).toLocaleString()}
            formatter={(val: any) => val !== null ? val.toFixed(3) + ' m' : 'N/A'}
            contentStyle={{ backgroundColor: '#f1f5f9', border: '1px solid #cbd5e1' }}
          />
          <Legend verticalAlign="bottom" />
          <Area dataKey="q90" fill="#bbf7d0" stroke="none" legendType="none" />
          <Area dataKey="q10" fill="white" stroke="none" legendType="none" />
          <Area dataKey="q75" fill="#4ade80" fillOpacity={0.4} stroke="none" legendType="none" />
          <Area dataKey="q25" fill="white" stroke="none" legendType="none" />
          <Line dataKey="q50" stroke="#16a34a" strokeWidth={2.5} dot={false} name="TFT Median (q50)" />
          <Line dataKey="actual" stroke="#dc2626" strokeWidth={1.8} strokeDasharray="5 3" dot={false} name="Observed" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}