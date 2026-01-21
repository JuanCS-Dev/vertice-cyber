/**
 * LogBuffer Utility
 * 
 * Implements a Circular Buffer for high-frequency log management.
 * Decouples log storage from React State to prevent re-render storms.
 * 
 * Architecture:
 * - Fixed capacity (default 1000)
 * - O(1) insertion
 * - Observer pattern for UI updates
 */

import { LogEntry } from '../types/telemetry';

export class LogBuffer {
  private buffer: LogEntry[];
  private capacity: number;
  private listeners: Set<() => void>;

  constructor(capacity: number = 1000) {
    this.capacity = capacity;
    this.buffer = [];
    this.listeners = new Set();
  }

  /**
   * Add a new log entry to the buffer.
   * Removes oldest entry if capacity is reached.
   */
  public add(entry: LogEntry): void {
    if (this.buffer.length >= this.capacity) {
      this.buffer.shift(); // Remove oldest (FIFO)
    }
    this.buffer.push(entry);
    this.notify();
  }

  /**
   * Get a snapshot of current logs.
   * @param limit Optional limit for the returned array (get last N logs)
   */
  public getSnapshot(limit?: number): LogEntry[] {
    if (limit && limit < this.buffer.length) {
      return this.buffer.slice(-limit);
    }
    return [...this.buffer]; // Return copy to prevent external mutation
  }

  /**
   * Subscribe to buffer updates.
   * Returns a cleanup function.
   */
  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Clear all logs.
   */
  public clear(): void {
    this.buffer = [];
    this.notify();
  }

  private notify(): void {
    this.listeners.forEach(listener => listener());
  }
}

// Global instance for singleton access if needed (though Context is preferred)
export const globalLogBuffer = new LogBuffer(2000);
