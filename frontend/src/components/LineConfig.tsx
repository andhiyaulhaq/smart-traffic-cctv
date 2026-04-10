"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { getLineConfig, updateLineConfig, LineConfig as LineConfigType } from "@/lib/api";
import { Settings2, Save } from "lucide-react";

export function LineConfig() {
  const [config, setConfig] = useState<LineConfigType>({
    x1: 0,
    y1: 0.5,
    x2: 1,
    y2: 0.5,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getLineConfig()
      .then((data) => {
        setConfig(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateLineConfig(config);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading config...</div>;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Settings2 className="w-5 h-5 text-primary" />
          <CardTitle>Virtual Line Configuration</CardTitle>
        </div>
        <CardDescription>
          Adjust the start (P1) and end (P2) points of the detection line.
          Coordinates are normalized (0.0 to 1.0).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Point 1 */}
          <div className="space-y-4">
            <h4 className="font-medium text-sm text-muted-foreground">Point 1 (Start)</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>X1: {config.x1.toFixed(2)}</Label>
              </div>
              <Slider
                value={[config.x1]}
                min={0}
                max={1}
                step={0.01}
                onValueChange={([val]) => setConfig({ ...config, x1: val })}
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Y1: {config.y1.toFixed(2)}</Label>
              </div>
              <Slider
                value={[config.y1]}
                min={0}
                max={1}
                step={0.01}
                onValueChange={([val]) => setConfig({ ...config, y1: val })}
              />
            </div>
          </div>

          {/* Point 2 */}
          <div className="space-y-4">
            <h4 className="font-medium text-sm text-muted-foreground">Point 2 (End)</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>X2: {config.x2.toFixed(2)}</Label>
              </div>
              <Slider
                value={[config.x2]}
                min={0}
                max={1}
                step={0.01}
                onValueChange={([val]) => setConfig({ ...config, x2: val })}
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Y2: {config.y2.toFixed(2)}</Label>
              </div>
              <Slider
                value={[config.y2]}
                min={0}
                max={1}
                step={0.01}
                onValueChange={([val]) => setConfig({ ...config, y2: val })}
              />
            </div>
          </div>
        </div>

        <Button 
          className="w-full" 
          onClick={handleSave} 
          disabled={saving}
        >
          {saving ? "Saving..." : "Apply Changes"}
          <Save className="w-4 h-4 ml-2" />
        </Button>
      </CardContent>
    </Card>
  );
}
