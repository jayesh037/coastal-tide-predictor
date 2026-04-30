import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { fetchStations, GeoJSONFeatureCollection } from '../api/client';

interface StationPickerProps {
  onSelect: (stationId: string, stationName: string) => void;
  selectedId: string | null;
}

export default function StationPicker({ onSelect, selectedId }: StationPickerProps) {
  const [data, setData] = useState<GeoJSONFeatureCollection | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    fetchStations()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError(true);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading stations...</div>;
  }

  if (error || !data) {
    return <div>Failed to load stations</div>;
  }

  return (
    <MapContainer center={[39.5, -98.35]} zoom={4} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {data.features.map((feature) => {
        const { station_id, name, state, lat, lon } = feature.properties;
        const isSelected = selectedId === station_id;
        return (
          <CircleMarker
            key={station_id}
            center={[lat, lon]}
            radius={6}
            pathOptions={{
              color: isSelected ? '#2563eb' : '#64748b',
              fillColor: isSelected ? '#2563eb' : '#64748b',
              fillOpacity: 0.8,
            }}
            eventHandlers={{
              click: () => onSelect(station_id, name),
            }}
          >
            <Popup>
              <strong>{name}</strong>
              <br />
              {state && <>{state}<br /></>}
              ID: {station_id}
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}