import React, { useState } from 'react';
import StationPicker from './components/StationPicker';
import ForecastChart from './components/ForecastChart';
import LiveFeed from './components/LiveFeed';
import { fetchForecast, ForecastResponse } from './api/client';

export default function App() {
  const [selectedStationId, setSelectedStationId] = useState<string | null>(null);
  const [selectedStationName, setSelectedStationName] = useState<string>('');
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loadingForecast, setLoadingForecast] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleStationSelect = (id: string, name: string) => {
    setSelectedStationId(id);
    setSelectedStationName(name);
    setError(null);
    setLoadingForecast(true);
    fetchForecast(id)
      .then((data) => {
        setForecast(data);
        setLoadingForecast(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoadingForecast(false);
      });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'row', height: '100vh', width: '100vw', margin: 0, padding: 0 }}>
      {/* LEFT PANEL */}
      <div
        style={{
          width: '35%',
          minWidth: '320px',
          background: '#0f172a',
          color: 'white',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          boxSizing: 'border-box'
        }}
      >
        <h1 style={{ fontSize: '20px', margin: 0 }}>🌊 Coastal Tide Predictor</h1>
        <p style={{ fontSize: '12px', color: '#94a3b8', margin: '4px 0 16px' }}>
          Powered by Temporal Fusion Transformer
        </p>

        {selectedStationId && (
          <div
            style={{
              background: '#1e293b',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '12px',
            }}
          >
            <div style={{ fontWeight: 'bold', color: 'white' }}>{selectedStationName}</div>
            <div style={{ color: '#64748b', fontSize: '12px', marginTop: '4px' }}>
              ID: {selectedStationId}
            </div>
          </div>
        )}

        <div style={{ flex: 1, minHeight: 0, borderRadius: '8px', overflow: 'hidden' }}>
          <StationPicker onSelect={handleStationSelect} selectedId={selectedStationId} />
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div
        style={{
          flex: 1,
          background: '#f8fafc',
          padding: '24px',
          overflowY: 'auto',
          boxSizing: 'border-box'
        }}
      >
        {!selectedStationId ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: '#94a3b8', fontSize: '18px' }}>Select a coastal station from the map</p>
          </div>
        ) : (
          <>
            {loadingForecast && (
              <p style={{ color: '#64748b' }}>Loading forecast for {selectedStationName}...</p>
            )}
            
            {error && (
              <p style={{ color: '#dc2626' }}>Error: {error}</p>
            )}
            
            {forecast && !loadingForecast && !error && (
              <>
                <ForecastChart forecast={forecast} stationName={selectedStationName} />
                
                <div
                  style={{
                    background: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '10px 16px',
                    margin: '16px 0',
                    fontSize: '13px',
                    color: '#475569',
                  }}
                >
                  Model: Temporal Fusion Transformer &nbsp;|&nbsp; Horizon: 7 days &nbsp;|&nbsp; Quantiles: 10 / 25 / 50 / 75 / 90
                </div>
                
                <LiveFeed stationId={selectedStationId} />
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}