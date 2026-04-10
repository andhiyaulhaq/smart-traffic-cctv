"use client";

import { VideoPlayer } from "@/components/VideoPlayer";
import { CounterCard } from "@/components/CounterCard";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useState, useEffect } from "react";
import { LineConfig } from "@/components/LineConfig";
import { HistoryChart } from "@/components/HistoryChart";
import { getTodayStats } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Activity } from "lucide-react";

export default function Home() {
  const { data, isConnected } = useWebSocket("ws://localhost:8000/ws/counts");
  const [counts, setCounts] = useState({ enter: 0, exit: 0 });
  const [lastEvent, setLastEvent] = useState<any>(undefined);

  useEffect(() => {
    if (data && data.type === "count_update") {
      setCounts(data.counts);
      if (data.event) {
        setLastEvent(data.event);
      }
    }
  }, [data]);

  // Initial fetch of today's totals
  useEffect(() => {
    getTodayStats().then(stats => {
      setCounts({ enter: stats.enter, exit: stats.exit });
    }).catch(console.error);
  }, []);

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-50 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-neutral-50 to-neutral-400 bg-clip-text text-transparent">
              Smart Traffic CCTV
            </h1>
            <Badge variant="outline" className="border-neutral-800 text-neutral-400 font-mono">
              v1.0.0
            </Badge>
          </div>
          <p className="text-neutral-400 max-w-2xl">
            Real‑time vehicle detection, tracking, and counting using computer vision at the edge.
          </p>
        </header>

        {/* Dashboard Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Feed */}
          <div className="lg:col-span-2 space-y-4">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-blue-500/20 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000" />
              <VideoPlayer />
            </div>
            
            <div className="flex items-center justify-between text-xs text-neutral-500 bg-neutral-900/50 p-3 rounded-xl border border-neutral-800 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" : "bg-yellow-500 animate-pulse"}`} />
                {isConnected ? "Live Stream Connected" : "Attempting Reconnection..."}
              </div>
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> Latency: 42ms</span>
                <span>Buffer: 0.4s</span>
              </div>
            </div>

            <HistoryChart />
          </div>

          {/* Sidebar / Analytics */}
          <div className="space-y-6">
            <CounterCard 
              enterCount={counts.enter} 
              exitCount={counts.exit} 
              lastEvent={lastEvent}
            />
            
            {/* Quick Stats Placeholder */}
            <div className="p-5 rounded-2xl border border-neutral-800 bg-neutral-900/30 space-y-4 backdrop-blur-md">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-widest">Session Overview</h3>
                <span className="text-[10px] text-green-500/80 font-mono px-2 py-0.5 rounded-full bg-green-500/10">Active</span>
              </div>
              <div className="grid grid-cols-1 gap-4">
                <div className="p-4 rounded-xl bg-neutral-900/60 border border-neutral-800/50">
                  <div className="text-xs text-neutral-500 mb-2">Total Volume (Today)</div>
                  <div className="text-3xl font-bold font-mono tracking-tighter text-blue-400">
                    {counts.enter + counts.exit}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-neutral-900/40 border border-neutral-800/50">
                    <div className="text-[10px] text-neutral-500 uppercase mb-1">Inflow</div>
                    <div className="text-lg font-semibold text-green-400">{counts.enter}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-neutral-900/40 border border-neutral-800/50">
                    <div className="text-[10px] text-neutral-500 uppercase mb-1">Outflow</div>
                    <div className="text-lg font-semibold text-red-400">{counts.exit}</div>
                  </div>
                </div>
              </div>
            </div>

            <LineConfig />
          </div>
        </div>
      </div>
    </main>
  );
}
