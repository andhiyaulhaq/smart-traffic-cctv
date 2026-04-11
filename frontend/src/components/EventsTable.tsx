"use client";

import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getRecentEvents, CountEvent } from "@/lib/api";
import { Badge } from "./ui/badge";

export function EventsTable({ lastEvent }: { lastEvent?: any }) {
  const [events, setEvents] = useState<CountEvent[]>([]);

  useEffect(() => {
    getRecentEvents().then(setEvents).catch(console.error);
  }, []);

  // Update table when a new event arrives via WebSocket
  useEffect(() => {
    if (lastEvent) {
      // Ensure the event matches the interface (backend might send raw dict)
      setEvents((prev) => [lastEvent, ...prev].slice(0, 50));
    }
  }, [lastEvent]);

  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900/40 overflow-hidden">
      <div className="p-4 border-b border-neutral-800 bg-neutral-900/60 flex items-center justify-between">
        <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-widest">Crossing Logs</h3>
        <Badge variant="outline" className="text-[10px] border-neutral-700 text-neutral-500">Live</Badge>
      </div>
      <Table>
        <TableHeader>
          <TableRow className="border-neutral-800 hover:bg-transparent">
            <TableHead className="text-neutral-500 font-mono text-[10px] uppercase">Time</TableHead>
            <TableHead className="text-neutral-500 font-mono text-[10px] uppercase">Dir</TableHead>
            <TableHead className="text-neutral-500 font-mono text-[10px] uppercase">Class</TableHead>
            <TableHead className="text-neutral-500 font-mono text-[10px] uppercase">ID</TableHead>
            <TableHead className="text-neutral-500 font-mono text-[10px] uppercase text-right">Conf</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-neutral-500 py-8 italic">
                No events recorded yet today.
              </TableCell>
            </TableRow>
          ) : (
            events.map((event, idx) => (
              <TableRow key={`${event.id}-${idx}`} className="border-neutral-800 hover:bg-neutral-800/30 group">
                <TableCell className="font-mono text-[10px] text-neutral-400">
                  {event.timestamp && !isNaN(Date.parse(event.timestamp))
                    ? new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                    : '--:--:--'}
                </TableCell>
                <TableCell>
                  <Badge 
                    variant="outline" 
                    className={`text-[9px] px-1.5 py-0 uppercase border-0 ${
                      event.direction === 'enter' 
                      ? 'text-green-500 bg-green-500/10' 
                      : 'text-red-500 bg-red-500/10'
                    }`}
                  >
                    {event.direction}
                  </Badge>
                </TableCell>
                <TableCell className="capitalize text-xs font-medium text-neutral-300">
                  {event.vehicle_class || 'unknown'}
                </TableCell>
                <TableCell className="font-mono text-[10px] text-neutral-500">#{event.track_id}</TableCell>
                <TableCell className="text-right font-mono text-[10px] text-neutral-300 group-hover:text-primary transition-colors">
                  {event.confidence !== undefined ? (event.confidence * 100).toFixed(0) : '0'}%
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
