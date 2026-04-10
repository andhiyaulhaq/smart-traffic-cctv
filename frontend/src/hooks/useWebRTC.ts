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
