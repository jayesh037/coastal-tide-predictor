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
import { ForecastResponse } from '../api/client';

interface ForecastChartProps {
  forecast: ForecastResponse | null;
  stationName: string;
}

export default function ForecastChart({ forecast, stationName }: ForecastChartProps) {
  if (!forecast) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '400px',
          color: '#94a3b8',
        }}
      >
        Select a station on the map to view its 7-day TFT forecast
      </div>
    );
  }

  const chartData = forecast.timestamps.map((t, i) => ({
    time: t,
    q10: forecast.q10[i],
    q25: forecast.q25[i],
    q50: forecast.q50[i],
    q75: forecast.q75[i],
    q90: forecast.q90[i],
    actual: forecast.actuals[i],
    dayLabel: i % 24 === 0 ? 'Day ' + (Math.floor(i / 24) + 1) : '',
  }));

  return (
    <div>
      <h3 style={{ margin: '0 0 8px', color: '#1e293b' }}>
        {stationName} — 7-Day TFT Forecast
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <XAxis
            dataKey="time"
            tickFormatter={(val, idx) => (idx % 24 === 0 ? 'Day ' + (Math.floor(idx / 24) + 1) : '')}
            interval={23}
          />
          <YAxis
            label={{ value: 'Water Level (m)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip formatter={(val: number) => val.toFixed(3) + ' m'} />
          <Legend verticalAlign="bottom" />

          {/* Ordered exactly as specified */}
          <Area dataKey="q90" fill="#bbf7d0" stroke="none" legendType="none" />
          <Area dataKey="q10" fill="white" stroke="none" legendType="none" />
          <Area dataKey="q75" fill="#4ade80" fillOpacity={0.4} stroke="none" legendType="none" />
          <Area dataKey="q25" fill="white" stroke="none" legendType="none" />
          <Line
            dataKey="q50"
            stroke="#16a34a"
            strokeWidth={2.5}
            dot={false}
            name="TFT Median (q50)"
          />
          <Line
            dataKey="actual"
            stroke="#dc2626"
            strokeWidth={1.8}
            strokeDasharray="5 3"
            dot={false}
            name="Observed"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}