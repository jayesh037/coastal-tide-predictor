export interface StationProperties {
  station_id: string
  name: string
  state: string | null
  lat: number
  lon: number
}

export interface GeoJSONFeature {
  type: "Feature"
  geometry: { type: "Point"; coordinates: [number, number] }
  properties: StationProperties
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection"
  features: GeoJSONFeature[]
}

export interface ObservationPoint {
  timestamp: string
  water_level: number
}

export interface ForecastResponse {
  station_id: string
  generated_at: string
  horizon_hours: number
  timestamps: string[]
  q10: number[]
  q25: number[]
  q50: number[]
  q75: number[]
  q90: number[]
  actuals: number[]
}

export interface HistoryResponse {
  station_id: string
  days: number
  observations: ObservationPoint[]
}

const BASE_URL = '/api'

export async function fetchStations(): Promise<GeoJSONFeatureCollection> {
  const response = await fetch(`${BASE_URL}/stations`)
  if (!response.ok) {
    throw new Error(`Failed to fetch stations: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

export async function fetchForecast(stationId: string): Promise<ForecastResponse> {
  const response = await fetch(`${BASE_URL}/forecast/${stationId}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch forecast for station ${stationId}: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

export async function fetchHistory(stationId: string, days: number): Promise<HistoryResponse> {
  const response = await fetch(`${BASE_URL}/history/${stationId}?days=${days}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch history for station ${stationId}: ${response.status} ${response.statusText}`)
  }
  return response.json()
}
