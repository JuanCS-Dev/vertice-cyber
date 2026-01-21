
import React, { useEffect, useState, useCallback } from 'react';
import { LiveLogTerminal, LogEntry } from '../LiveLogTerminal';
import { eventStream } from '../../services/eventStream';

interface LiveTerminalProps {
    filter?: string | ((event: any) => boolean);
}

export const LiveTerminal: React.FC<LiveTerminalProps> = ({ filter }) => {
    const [logs, setLogs] = useState<LogEntry[]>([]);

    // Subscribe to Neural Mesh
    useEffect(() => {
        const handleEvent = (event: any) => {
            // Apply filter if present
            if (filter) {
                if (typeof filter === 'string') {
                    // Loose matching for agent IDs (e.g. "osint" matches "osint_hunter" or "osint-123")
                    if (!event.source?.toLowerCase().includes(filter.toLowerCase())) return;
                }
                else if (typeof filter === 'function' && !filter(event)) return;
            }

            // Map event to LogEntry
            const entry: LogEntry = {
                timestamp: formatTimestamp(event.timestamp),
                level: mapLevel(event.level || 'info'),
                source: event.source || 'SYSTEM',
                message: extractMessage(event)
            };

            setLogs(prev => [...prev, entry].slice(-500)); // Keep last 500
        };

        // Subscribe to everything
        const unsub = eventStream.subscribe('*', handleEvent);

        return () => {
            unsub();
        };
    }, [filter]);

    const handleClear = useCallback(() => {
        setLogs([]);
    }, []);

    return (
        <div className="h-full w-full">
            <LiveLogTerminal
                logs={logs}
                onClear={handleClear}
            />
        </div>
    );
};

// ... Helpers ...
function formatTimestamp(iso: string): string {
    if (!iso) return new Date().toISOString().split('T')[1].slice(0, 8);
    try {
        return new Date(iso).toISOString().split('T')[1].slice(0, 8); // HH:mm:ss
    } catch {
        return iso;
    }
}

function mapLevel(level: string): 'info' | 'warn' | 'error' | 'success' | 'debug' {
    if (!level) return 'info';
    const l = level.toLowerCase();
    if (l.includes('err') || l.includes('fail')) return 'error';
    if (l.includes('warn')) return 'warn';
    if (l.includes('ok') || l.includes('succ')) return 'success';
    if (l.includes('dbg')) return 'debug';
    return 'info';
}

function extractMessage(event: any): string {
    if (event.payload?.message) return event.payload.message;
    if (typeof event.payload === 'string') return event.payload;
    if (event.message) return event.message;
    return `${event.type} // ${JSON.stringify(event.payload || {})}`;
}
