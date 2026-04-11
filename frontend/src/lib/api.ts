export interface LineConfig {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface HourlyCount {
  hour: string;
  count: number;
}

export interface StatsResponse {
  enter: number;
  exit: number;
  hourly_counts: HourlyCount[];
}

export interface CountEvent {
  id: number;
  timestamp: string;
  direction: string;
  vehicle_class: string;
  track_id: number;
  confidence: number;
}

const API_BASE = "/api"; // Assumes Next.js rewrites are configured

export const getLineConfig = async (): Promise<LineConfig> => {
  const res = await fetch(`${API_BASE}/line`);
  if (!res.ok) throw new Error("Failed to fetch line config");
  return res.json();
};

export const updateLineConfig = async (config: LineConfig): Promise<void> => {
  const res = await fetch(`${API_BASE}/line`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!res.ok) throw new Error("Failed to update line config");
};

export const getTodayStats = async (): Promise<StatsResponse> => {
  const res = await fetch(`${API_BASE}/stats/today`);
  if (!res.ok) throw new Error("Failed to fetch statistics");
  return res.json();
};

export const getRecentEvents = async (limit: number = 50): Promise<CountEvent[]> => {
  const res = await fetch(`${API_BASE}/events?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch events");
  return res.json();
};
