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
