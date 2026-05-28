import React, { useState, useEffect } from 'react';
import StationDropdown from './components/StationDropdown';
import StationMap from './components/StationMap';
import ForecastChart from './components/ForecastChart';
import HistoryChart from './components/HistoryChart';
import LiveFeed from './components/LiveFeed';
import { 
  fetchStations, 
  fetchForecast, 
  fetchHistory,
  ForecastResponse, 
  ForecastHistoryItem,
  StationProperties
} from './api/client';
import './App.css';

export default function App() {
  const [stations, setStations] = useState<StationProperties[]>([]);
  const [selectedStationId, setSelectedStationId] = useState<string | null>(null);
  const [selectedStationName, setSelectedStationName] = useState<string>('');
  
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [history, setHistory] = useState<ForecastHistoryItem[]>([]);
  
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStations()
      .then((data) => {
        // Data comes as FeatureCollection
        const props = data.features.map(f => f.properties);
        setStations(props);
      })
      .catch(console.error);
  }, []);

  const handleStationSelect = (id: string, name: string) => {
    setSelectedStationId(id);
    setSelectedStationName(name);
    setError(null);
    setLoading(true);

    Promise.all([
      fetchForecast(id),
      fetchHistory(id, 30)
    ])
      .then(([forecastData, historyData]) => {
        setForecast(forecastData);
        setHistory(historyData);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch data');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="app-container">
      {/* LEFT PANEL */}
      <div className="sidebar">
        <h1 style={{ fontSize: '20px', margin: 0 }}>🌊 Coastal Tide Predictor</h1>
        <p style={{ fontSize: '12px', color: '#94a3b8', margin: '4px 0 16px' }}>
          Powered by Temporal Fusion Transformer
        </p>

        <StationDropdown 
          stations={stations} 
          selectedId={selectedStationId} 
          onSelect={handleStationSelect} 
        />

        <div className="map-wrapper">
          <StationMap 
            stations={stations}
            selectedStationId={selectedStationId}
            onSelect={handleStationSelect}
          />
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="main-content">
        {!selectedStationId ? (
          <div className="empty-state">
            <p>Select a coastal station from the map or dropdown to view its forecast and history</p>
          </div>
        ) : (
          <div className="dashboard">
            {loading && (
              <div className="loading-state">Loading data for {selectedStationName}...</div>
            )}
            
            {error && (
              <div className="error-state">Error: {error}</div>
            )}
            
            {!loading && !error && (
              <>
                <div className="dashboard-header">
                  <h2>{selectedStationName}</h2>
                  <span className="station-id">ID: {selectedStationId}</span>
                </div>

                <div className="charts-container">
                  <div className="chart-card">
                    <ForecastChart forecast={forecast} stationName={selectedStationName} />
                  </div>
                  <div className="chart-card">
                    <HistoryChart history={history} stationName={selectedStationName} />
                  </div>
                </div>

                <div className="live-feed-container">
                  <LiveFeed stationId={selectedStationId} />
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}