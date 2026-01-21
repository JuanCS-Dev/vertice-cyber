/**
 * Latency Widget
 * 
 * Visualizes system latency using SVG graphs.
 * Consumes real telemetry data.
 */

import React, { useEffect, useState, useMemo } from 'react';
import { useTelemetry } from '../../contexts/TelemetryContext';

export const LatencyWidget: React.FC = () => {
  const { metrics } = useTelemetry();
  const [history, setHistory] = useState<number[]>(new Array(10).fill(0));

  // Update history when latency changes
  useEffect(() => {
    setHistory(prev => {
        const next = [...prev, metrics.latency];
        return next.slice(-10); // Keep last 10 points
    });
  }, [metrics.latency]);

  const pathD = useMemo(() => {
    return `M 0 20 ${history.map((p, i) => {
        // Normalize: 0ms -> 40y, 100ms -> 0y
        const y = Math.max(0, 40 - (p / 100) * 40); 
        return `L ${i * 10} ${y}`;
    }).join(' ')}`;
  }, [history]);

  return (
    <div className="flex flex-col items-end">
        <span className="text-[8px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">
            Ping: {metrics.latency.toFixed(0)}ms
        </span>
        <svg className="w-24 h-6 text-secondary opacity-50" viewBox="0 0 100 40" preserveAspectRatio="none">
            <path
                d={pathD}
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="vector-effect-non-scaling-stroke"
            />
        </svg>
    </div>
  );
};
