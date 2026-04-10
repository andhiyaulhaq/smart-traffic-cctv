import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowDownCircle, ArrowUpCircle, Car } from "lucide-react";

interface CounterCardProps {
  enterCount: number;
  exitCount: number;
  lastEvent?: {
    direction: string;
    class_name: string;
    track_id: number;
  };
}

export function CounterCard({ enterCount, exitCount, lastEvent }: CounterCardProps) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    if (lastEvent) {
      setPulse(true);
      const timer = setTimeout(() => setPulse(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [lastEvent]);

  return (
    <Card className={`overflow-hidden transition-all duration-300 ${pulse ? 'ring-2 ring-primary bg-primary/5' : ''}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Car className="w-4 h-4" />
            Live Traffic Counters
          </CardTitle>
          <Badge variant={pulse ? "default" : "secondary"} className="animate-in fade-in zoom-in duration-300">
            {pulse ? "NEW CROSSING" : "LIVE"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-green-500">
              <ArrowDownCircle className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase">Entered</span>
            </div>
            <div className="text-3xl font-bold tracking-tight">
              {enterCount}
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-red-500">
              <ArrowUpCircle className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase">Exited</span>
            </div>
            <div className="text-3xl font-bold tracking-tight">
              {exitCount}
            </div>
          </div>
        </div>

        {lastEvent && (
          <div className="mt-4 pt-4 border-t text-[10px] text-muted-foreground flex justify-between items-center animate-in slide-in-from-bottom-2 duration-500">
            <span>Last Detected: <span className="font-semibold text-foreground uppercase">{lastEvent.class_name}</span></span>
            <span>ID: <span className="font-mono text-foreground font-semibold">#{lastEvent.track_id}</span></span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
