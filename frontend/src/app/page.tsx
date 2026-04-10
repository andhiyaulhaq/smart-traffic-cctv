"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const [status, setStatus] = useState<string>("Loading...");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setStatus(data.message))
      .catch(() => setStatus("Error connecting to backend"));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-50">
      <Card className="w-96 shadow-lg border-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl text-slate-800">System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-3 py-4">
            <div 
              className={`h-4 w-4 rounded-full ${
                status === 'Backend is running!' 
                ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' 
                : 'bg-amber-500 animate-pulse'
              }`}
            ></div>
            <p className="font-semibold text-slate-700 text-lg">{status}</p>
          </div>
          <div className="mt-2 text-xs text-slate-400 font-medium uppercase tracking-wider">
            Smart Traffic CCTV - Phase 0 Scaffold
          </div>
        </CardContent>
      </Card>
    </main>
  );
}

