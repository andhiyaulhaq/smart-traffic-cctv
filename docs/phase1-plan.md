# Phase 1: Basic WebRTC Streaming - Technical Implementation Plan

## Objective
Establish a successful WebRTC connection to stream *unprocessed, synthetic* video frames directly from the FastAPI backend to the Next.js frontend. This proves the low-latency communication pipeline works before introducing real video or computer vision models.

## 1. Backend – WebRTC Setup

1. **Install Dependencies:**
   Navigate into `backend/` and add the required WebRTC packages using `uv`. We need `aiortc` for WebRTC, and `numpy` plus `av` for generating the synthetic video frames.
   ```bash
   cd backend
   uv add aiortc numpy av
   ```

2. **Implement Synthetic Video Track (`app/services/webrtc.py`):**
   Create a dummy video track that generates a changing color pattern to visually verify the stream is live.
   ```python
   import asyncio
   import numpy as np
   from av import VideoFrame
   from aiortc import VideoStreamTrack
   import time

   class SyntheticVideoTrack(VideoStreamTrack):
       """
       A video stream track that generates synthetic frames.
       """
       def __init__(self):
           super().__init__()
           self.counter = 0

       async def recv(self):
           pts, time_base = await self.next_timestamp()
           
           # Generate a synthetic frame: a simple colored square that shifts color
           self.counter += 1
           img = np.zeros((480, 640, 3), dtype=np.uint8)
           
           # Change color based on counter to create a visual effect
           r = int((np.sin(self.counter * 0.1) + 1) * 127)
           g = int((np.cos(self.counter * 0.1) + 1) * 127)
           img[:] = (r, g, 150)  # BGR format
           
           # Convert to av.VideoFrame
           frame = VideoFrame.from_ndarray(img, format="bgr24")
           frame.pts = pts
           frame.time_base = time_base
           
           return frame
   ```

3. **Implement WebRTC Endpoint (`app/main.py`):**
   Add endpoints and schemas to receive an SDP offer and return an SDP answer.
   ```python
   import asyncio
   from fastapi import FastAPI
   from pydantic import BaseModel
   from aiortc import RTCPeerConnection, RTCSessionDescription
   from app.services.webrtc import SyntheticVideoTrack

   app = FastAPI(title="Smart Traffic CCTV API")

   # Schema for WebRTC Offer
   class Offer(BaseModel):
       sdp: str
       type: str

   # Store peer connections to manage their lifecycle
   pcs = set()

   @app.post("/offer")
   async def offer(offer_data: Offer):
       offer = RTCSessionDescription(sdp=offer_data.sdp, type=offer_data.type)
       pc = RTCPeerConnection()
       pcs.add(pc)

       @pc.on("connectionstatechange")
       async def on_connectionstatechange():
           print(f"Connection state is {pc.connectionState}")
           if pc.connectionState == "failed" or pc.connectionState == "closed":
               pcs.discard(pc)

       # Add the synthetic video track
       pc.addTrack(SyntheticVideoTrack())

       await pc.setRemoteDescription(offer)
       answer = await pc.createAnswer()
       await pc.setLocalDescription(answer)

       return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

   @app.on_event("shutdown")
   async def on_shutdown():
       coros = [pc.close() for pc in pcs]
       await asyncio.gather(*coros)
       pcs.clear()

   @app.get("/health")
   async def health_check():
       return {"status": "ok", "message": "Backend is running!"}
   ```

## 2. Frontend – WebRTC Client Setup

1. **Architecture Decision:**
   While the original design mentioned `simple-peer`, configuring polyfills for Node.js defaults in modern Next.js (App Router) can introduce unnecessary friction. Using the native browser `RTCPeerConnection` API is cleaner, modern, and does not require additional NPM packages.

2. **Create WebRTC Hook (`src/hooks/useWebRTC.ts`):**
   Implement a custom hook to manage the connection lifecycle, exchange SDP via the REST proxy (`/api/offer`), and return the remote `MediaStream`.
   ```typescript
   import { useEffect, useRef, useState } from 'react';

   export function useWebRTC() {
     const [stream, setStream] = useState<MediaStream | null>(null);
     const [error, setError] = useState<string | null>(null);
     const pcRef = useRef<RTCPeerConnection | null>(null);

     useEffect(() => {
       const initWebRTC = async () => {
         try {
           const pc = new RTCPeerConnection({
             iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
           });
           pcRef.current = pc;

           // Listen for incoming remote tracks from the backend
           pc.ontrack = (event) => {
             if (event.streams && event.streams[0]) {
               setStream(event.streams[0]);
             } else {
               const newStream = new MediaStream([event.track]);
               setStream(newStream);
             }
           };

           // We are only receiving video in this phase, establish a recvonly transceiver
           pc.addTransceiver('video', { direction: 'recvonly' });

           // Create offer
           const offer = await pc.createOffer();
           await pc.setLocalDescription(offer);

           // Send offer to backend
           const response = await fetch('/api/offer', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({
               sdp: pc.localDescription?.sdp,
               type: pc.localDescription?.type,
             }),
           });

           if (!response.ok) throw new Error('Failed to fetch SDP answer');

           // Receive and apply answer
           const answer = await response.json();
           await pc.setRemoteDescription(new RTCSessionDescription(answer));

         } catch (err: any) {
           setError(err.message);
           console.error("WebRTC Error:", err);
         }
       };

       initWebRTC();

       // Cleanup on unmount
       return () => {
         pcRef.current?.close();
       };
     }, []);

     return { stream, error };
   }
   ```

3. **Create VideoPlayer Component (`src/components/VideoPlayer.tsx`):**
   ```tsx
   "use client";

   import { useEffect, useRef } from "react";
   import { useWebRTC } from "@/hooks/useWebRTC";
   import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

   export default function VideoPlayer() {
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
   ```

4. **Integrate into the Dashboard (`src/app/page.tsx`):**
   Update the home page to include the generic health status and the new video stream player side-by-side or stacked.
   ```tsx
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
         <h1 className="text-3xl font-bold text-slate-800">Smart Traffic CCTV</h1>
         
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
   ```

## 3. Execution and Verification Plan
1. **Apply Changes and Install Dependencies:**
   Run `uv add aiortc numpy av` in `backend/` as outlined above. Ensure `app/services` directory exists.

2. **Start the Backend:**
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload --port 8000
   ```

3. **Start the Frontend:**
   ```bash
   cd frontend
   pnpm dev --port 3000
   ```

4. **Verify Functionality:**
   - Open `http://localhost:3000` in the browser.
   - The UI should show "Connecting to stream..." inside the black player box.
   - Once the WebRTC negotiation finishes (sub-second), the `VideoPlayer` will render the synthetic video frames generated by the backend API.
   - Watch for shifting color patterns in the video box indicating active frame delivery.
   - The "System Status" card should continue to indicate "Backend is running!".
