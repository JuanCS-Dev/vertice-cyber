/**
 * Telemetry Types
 * Centralized definitions for system observability.
 * 
 * @module Telemetry
 */

export type LogLevel = 'info' | 'warn' | 'error' | 'success' | 'debug';

export interface LogEntry {
  id: string; // Unique ID for keying
  timestamp: string;
  level: LogLevel;
  source: string;
  message: string;
  metadata?: Record<string, unknown>;
}

export interface SystemMetrics {
  latency: number; // ms
  cpuLoad: number; // percentage
  memoryUsage: string; // formatted string
  activeThreads: number;
}
