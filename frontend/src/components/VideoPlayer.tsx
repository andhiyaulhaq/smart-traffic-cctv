"use client";

import { useEffect, useRef } from "react";
import { useWebRTC } from "@/hooks/useWebRTC";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export function VideoPlayer() {
  const { stream, error } = useWebRTC();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return (
    <Card className="w-full max-w-3xl shadow-lg border-slate-200 overflow-hidden">
      <CardHeader className="bg-slate-50 border-b">
        <CardTitle className="text-xl">Live Stream</CardTitle>
      </CardHeader>
      <CardContent className="p-0 bg-black aspect-video flex items-center justify-center relative">
        {error ? (
          <p className="text-red-500 font-medium">Error: {error}</p>
        ) : stream ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-slate-400 animate-pulse">Connecting to stream...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
