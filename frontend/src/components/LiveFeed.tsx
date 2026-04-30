import React, { useEffect, useState } from 'react';

interface LiveFeedProps {
  stationId: string | null;
}

interface Reading {
  station_id: string;
  timestamp: string;
  water_level: number | null; // metadata might not include real-time water levels
}

export default function LiveFeed({ stationId }: LiveFeedProps) {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [connected, setConnected] = useState<boolean>(false);

  useEffect(() => {
    if (!stationId) {
      setReadings([]);
      setConnected(false);
      return;
    }

    const ws = new WebSocket('ws://localhost:8000/ws/live/' + stationId);
    
    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (e) => {
      try {
        const data: Reading = JSON.parse(e.data);
        setReadings((prev) => [data, ...prev].slice(0, 10));
      } catch (err) {
        console.error('Failed to parse websocket message', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [stationId]);

  if (!stationId) {
    return <div style={{ color: '#94a3b8' }}>Select a station to start live feed</div>;
  }

  const hasData = readings.length > 0;
  const latest = hasData ? readings[0] : null;

  return (
    <div
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        padding: '16px',
        backgroundColor: '#f8fafc',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h4 style={{ margin: 0, color: '#1e293b' }}>Live Feed</h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', color: '#475569' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: connected ? '#22c55e' : '#94a3b8',
            }}
          />
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {hasData && latest ? (
        <div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#0f172a', marginBottom: '4px' }}>
            {latest.water_level !== null && latest.water_level !== undefined ? latest.water_level.toFixed(3) + ' m' : 'N/A'}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '16px' }}>
            as of {new Date(latest.timestamp).toLocaleTimeString()}
          </div>

          <table style={{ width: '100%', fontSize: '14px', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #cbd5e1', color: '#475569' }}>
                <th style={{ paddingBottom: '8px' }}>Time</th>
                <th style={{ paddingBottom: '8px' }}>Water Level</th>
              </tr>
            </thead>
            <tbody>
              {readings.slice(0, 5).map((r, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '8px 0', color: '#334155' }}>
                    {new Date(r.timestamp).toLocaleTimeString()}
                  </td>
                  <td style={{ padding: '8px 0', color: '#334155', fontWeight: '500' }}>
                    {r.water_level !== null && r.water_level !== undefined ? r.water_level.toFixed(3) + ' m' : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ color: '#64748b', fontSize: '14px' }}>Waiting for data...</div>
      )}
    </div>
  );
}