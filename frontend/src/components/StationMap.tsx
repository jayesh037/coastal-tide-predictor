import React, { useEffect, useRef } from 'react';
import { StationProperties } from '../api/client';

interface StationMapProps {
  stations: StationProperties[];
  selectedStationId: string | null;
  onSelect: (id: string, name: string) => void;
}

export default function StationMap({ stations, selectedStationId, onSelect }: StationMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  useEffect(() => {
    // @ts-ignore
    if (!window.mapboxgl) return;
    
    // @ts-ignore
    window.mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrX6tCrB12ww';

    if (mapContainer.current && !mapRef.current) {
      // @ts-ignore
      mapRef.current = new window.mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-98.35, 39.5], // Center of US
        zoom: 3
      });
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    // Clear old markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    // @ts-ignore
    const mapboxgl = window.mapboxgl;

    stations.forEach(station => {
      const isSelected = station.id === selectedStationId;
      
      // Create a DOM element for the marker
      const el = document.createElement('div');
      el.style.width = isSelected ? '16px' : '12px';
      el.style.height = isSelected ? '16px' : '12px';
      el.style.backgroundColor = isSelected ? '#2563eb' : '#64748b';
      el.style.borderRadius = '50%';
      el.style.border = '2px solid white';
      el.style.cursor = 'pointer';
      el.style.transition = 'all 0.2s ease';

      if (isSelected) {
        el.style.boxShadow = '0 0 0 4px rgba(37, 99, 235, 0.3)';
        el.style.zIndex = '10';
      }

      el.addEventListener('click', () => {
        onSelect(station.id, station.name);
      });

      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
        `<strong>${station.name}</strong><br/>` +
        `${station.state ? station.state + '<br/>' : ''}` +
        `ID: ${station.id}`
      );

      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([station.lon, station.lat])
        .setPopup(popup)
        .addTo(mapRef.current);

      markersRef.current.push(marker);
    });

    if (selectedStationId) {
      const selected = stations.find(s => s.id === selectedStationId);
      if (selected) {
        mapRef.current.flyTo({
          center: [selected.lon, selected.lat],
          zoom: 7,
          essential: true
        });
      }
    }
  }, [stations, selectedStationId, onSelect]);

  return <div ref={mapContainer} style={{ width: '100%', height: '100%', minHeight: '300px', borderRadius: '8px' }} />;
}