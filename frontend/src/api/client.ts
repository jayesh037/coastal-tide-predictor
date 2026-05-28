import axios from 'axios';

export interface StationProperties {
  id: string; // Updated from station_id based on GET /api/stations response
  name: string;
  state: string | null;
  lat: number;
  lon: number;
  timezone: string;
  region: string;
}

export interface GeoJSONFeature {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: StationProperties;
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}

export interface ForecastResponse {
  station_id: string;
  generated_at: string;
  horizon_hours: number;
  timestamps: string[];
  q10: number[];
  q25: number[];
  q50: number[];
  q75: number[];
  q90: number[];
  actuals: number[];
}

export interface ForecastHistoryItem {
  id: number;
  station_id: string;
  timestamp: string;
  q10: number;
  q25: number;
  q50: number;
  q75: number;
  q90: number;
  actual_water_level: number | null;
  created_at: string;
}

const api = axios.create({
  baseURL: '/api'
});

export async function fetchStations(): Promise<GeoJSONFeatureCollection> {
  const response = await api.get<GeoJSONFeatureCollection>('/stations');
  return response.data;
}

export async function fetchForecast(stationId: string): Promise<ForecastResponse> {
  const response = await api.get<ForecastResponse>(`/forecast/${stationId}`);
  return response.data;
}

export async function fetchHistory(stationId: string, days: number = 30): Promise<ForecastHistoryItem[]> {
  const response = await api.get<ForecastHistoryItem[]>(`/history/${stationId}?days=${days}`);
  return response.data;
}
