/**
 * Telemetry Context
 * 
 * Provides global access to system metrics, logs, and connection status.
 * Acts as the bridge between the EventStream (WebSocket) and the UI.
 */

import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { LogBuffer, globalLogBuffer } from '../utils/LogBuffer';
import { eventStream } from '../services/eventStream';
import { LogEntry, SystemMetrics } from '../types/telemetry';

interface TelemetryContextState {
  isConnected: boolean;
  metrics: SystemMetrics;
  logBuffer: LogBuffer;
  addLog: (message: string, level?: LogEntry['level'], source?: string) => void;
}

const TelemetryContext = createContext<TelemetryContextState | null>(null);

export const TelemetryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    latency: 0,
    cpuLoad: 0,
    memoryUsage: '0/0 MB',
    activeThreads: 0
  });

  // LogBuffer is instantiated once per app lifecycle (or imported globally)
  const logBuffer = globalLogBuffer;

  const addLog = useMemo(() => (message: string, level: LogEntry['level'] = 'info', source: string = 'SYSTEM') => {
    const entry: LogEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toLocaleTimeString(),
      level,
      source,
      message
    };
    logBuffer.add(entry);
  }, [logBuffer]);

  useEffect(() => {
    // 1. Initialize Connection
    eventStream.connect();

    // 2. Set up Subscriptions
    const unsubConnect = eventStream.on('system.connected', () => {
      setIsConnected(true);
      addLog('Neural Link Established', 'success', 'NETWORK');
    });

    const unsubDisconnect = eventStream.on('system.disconnected', () => {
      setIsConnected(false);
      addLog('Neural Link Severed', 'error', 'NETWORK');
    });

    // Capture ALL events for logging (filtered by importance if needed)
    const unsubAll = eventStream.on('*', (event: any) => {
      // Avoid logging the log events themselves if we had a loop
      const type = event.type || 'unknown';
      const source = (event.source || 'MCP').toUpperCase();
      
      let level: LogEntry['level'] = 'info';
      if (type.includes('error') || type.includes('failed')) level = 'error';
      if (type.includes('warn')) level = 'warn';
      if (type.includes('success') || type.includes('completed')) level = 'success';

      // Human-readable message construction
      const message = event.message || type.replace(/\./g, ' ').toUpperCase();
      
      // Don't log every single heartbeat to avoid noise, unless debug
      if (type !== 'heartbeat') {
        addLog(message, level, source);
      }
    });

    // Heartbeat/Metrics handler
    const unsubHeartbeat = eventStream.on('heartbeat', (event: any) => {
       // Update latency/metrics from heartbeat payload if available
       // Or calculate RTT if we implemented ping
       if (event.metrics) {
         setMetrics(prev => ({
           ...prev,
           ...event.metrics
         }));
       }
    });

    return () => {
      unsubConnect();
      unsubDisconnect();
      unsubAll();
      unsubHeartbeat();
      // eventStream is a singleton, we do NOT disconnect it here
      // as other providers might rely on it.
    };
  }, [addLog]);

  const value = useMemo(() => ({
    isConnected,
    metrics,
    logBuffer,
    addLog
  }), [isConnected, metrics, logBuffer, addLog]);

  return (
    <TelemetryContext.Provider value={value}>
      {children}
    </TelemetryContext.Provider>
  );
};

export const useTelemetry = () => {
  const context = useContext(TelemetryContext);
  if (!context) {
    throw new Error('useTelemetry must be used within a TelemetryProvider');
  }
  return context;
};
