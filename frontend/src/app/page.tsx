"use client";

import { VideoPlayer } from "@/components/VideoPlayer";
import { CounterCard } from "@/components/CounterCard";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useState, useEffect } from "react";

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
            
            <div className="flex items-center justify-between text-xs text-neutral-500 bg-neutral-900/50 p-3 rounded-lg border border-neutral-800">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                Live Stream Connection: {isConnected ? "Connected" : "Reconnecting..."}
              </div>
              <div>Buffer: 0.4s</div>
            </div>
          </div>

          {/* Sidebar / Analytics */}
          <div className="space-y-6">
            <CounterCard 
              enterCount={counts.enter} 
              exitCount={counts.exit} 
              lastEvent={lastEvent}
            />
            
            {/* Quick Stats Placeholder */}
            <div className="p-4 rounded-xl border border-neutral-800 bg-neutral-900/30 space-y-4">
              <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider">Session Overview</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 rounded-lg bg-neutral-900/50">
                  <div className="text-xs text-neutral-500 mb-1">Total Vehicles</div>
                  <div className="text-xl font-bold">{counts.enter + counts.exit}</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-neutral-900/50">
                  <div className="text-xs text-neutral-500 mb-1">Avg Speed</div>
                  <div className="text-xl font-bold">--</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
