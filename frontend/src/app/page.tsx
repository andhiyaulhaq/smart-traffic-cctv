"use client";

import { useEffect, useState } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const [status, setStatus] = useState<string>("Loading...");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setStatus(data.message))
      .catch((err) => setStatus("Error connecting to backend"));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center p-8 lg:p-24 bg-slate-50 gap-8">
      <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 lg:text-5xl">
        Smart Traffic CCTV
      </h1>
      
      <VideoPlayer />

      <Card className="w-96 shadow-sm border-slate-200">
        <CardHeader>
          <CardTitle className="text-lg">System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <div className={`h-3 w-3 rounded-full ${status === 'Backend is running!' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`}></div>
            <p className="font-medium text-slate-700">{status}</p>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}

