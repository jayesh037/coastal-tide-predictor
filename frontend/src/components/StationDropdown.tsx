import React from 'react';
import { StationProperties } from '../api/client';

interface StationDropdownProps {
  stations: StationProperties[];
  selectedId: string | null;
  onSelect: (id: string, name: string) => void;
}

export default function StationDropdown({ stations, selectedId, onSelect }: StationDropdownProps) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <label htmlFor="station-select" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        Select Station
      </label>
      <select
        id="station-select"
        value={selectedId || ''}
        onChange={(e) => {
          const selected = stations.find(s => s.id === e.target.value);
          if (selected) {
            onSelect(selected.id, selected.name);
          }
        }}
        style={{
          width: '100%',
          padding: '10px',
          borderRadius: '6px',
          border: '1px solid #cbd5e1',
          background: 'white',
          color: '#0f172a',
          fontSize: '14px',
          outline: 'none'
        }}
      >
        <option value="" disabled>-- Select a coastal station --</option>
        {stations.map((station) => (
          <option key={station.id} value={station.id}>
            {station.name} {station.state ? `, ${station.state}` : ''} ({station.id})
          </option>
        ))}
      </select>
    </div>
  );
}