/**
 * useMCPAgents Hook
 * Gerencia estado dos agents MCP com real-time updates via WebSocket
 */

import { useState, useEffect, useCallback } from 'react';
import { mcpClient } from '../services/mcpClient';
import { eventStream } from '../services/eventStream';
import { Agent, AgentStatus, Threat } from '../types';
// Types are inline - MCP bridge provides the data
import { generateAgents } from '../types'; // For 3D positions

export interface LogObject {
    timestamp: string;
    level: 'info' | 'warn' | 'error' | 'success' | 'debug';
    source: string;
    message: string;
}

export interface UseMCPAgentsReturn {
    agents: Agent[];
    threats: Threat[];
    logs: LogObject[];
    isLoading: boolean;
    isConnected: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

// Mapping of tool categories to human-readable roles
const CATEGORY_TO_ROLE: Record<string, 'Guardian' | 'Hunter' | 'Analyst'> = {
    'security': 'Guardian',
    'intelligence': 'Analyst',
    'recon': 'Hunter',
    'compliance': 'Guardian',
    'offensive': 'Hunter',
    'defense': 'Guardian',
    'malware': 'Analyst',
    'forensics': 'Analyst',
    'osint': 'Hunter',
    'ethics': 'Guardian',
    'network': 'Guardian',
};

export function useMCPAgents(): UseMCPAgentsReturn {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [threats, setThreats] = useState<Threat[]>([]);
    const [logs, setLogs] = useState<LogObject[]>([{
        timestamp: new Date().toLocaleTimeString(),
        level: 'info',
        source: 'SYSTEM',
        message: 'Neural Core Initializing...'
    }]);
    const [isLoading, setIsLoading] = useState(true);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Add structured log entry
    const addLog = useCallback((msg: string, level: LogObject['level'] = 'info', source: string = 'SYSTEM') => {
        setLogs(prev => [...prev.slice(-49), {
            timestamp: new Date().toLocaleTimeString(),
            level,
            source,
            message: msg
        }]);
    }, []);

    /**
     * Fetch agents from MCP and merge with 3D positions
     */
    const fetchAgents = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Fetch real metrics from backend
            // Note: This endpoint now returns the unified source of truth (DB + System Metrics)
            const response = await fetch('/api/v1/agents/metrics');
            if (!response.ok) throw new Error('Failed to fetch agent metrics');

            const data = await response.json();

            // Map backend data to frontend Agent interface
            const realAgents: Agent[] = data.agents.map((a: any, index: number) => ({
                id: a.id,
                name: a.name,
                role: 'Specialist', // Could be derived from type if needed
                status: a.status,
                health: a.health,
                cpuLoad: a.cpuLoad,
                memoryMB: a.memoryMB,
                tasksCompleted: a.tasksCompleted,
                // Keep 3D position logic if needed, or let UI handle it
                position: [0, 0, 0] // Placeholder, UI layout handles this
            }));

            // If we have 3D visualization generation logic, apply it here
            // merging simple list with positions
            const positionedAgents = generateAgents(realAgents.length).map((pos, i) => ({
                ...realAgents[i],
                ...pos // Overwrite ID/Name/etc if generateAgents is mock-heavy, careful!
                // Actually generateAgents returns full mock objects. 
                // We should just assume generateAgents provides positions.
                // For now, let's trust the backend data.
            }));

            // Fix: generateAgents returns full mock objects. We want just layout.
            // Let's rely on the backend data primarily.
            setAgents(realAgents);
            setIsConnected(true);

        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Failed to fetch agents';
            setError(errorMsg);
            addLog(`❌ Error: ${errorMsg}`);
            // Do NOT fallback to random data - show error state
        } finally {
            setIsLoading(false);
        }
    }, [addLog]);

    /**
     * Handle MCP events from WebSocket
     */
    useEffect(() => {
        // Connect to WebSocket
        eventStream.connect();

        // Connection status
        const unsubConnect = eventStream.on('_connected', () => {
            setIsConnected(true);
            addLog('🔌 Connected to MCP Event Stream');
        });

        const unsubDisconnect = eventStream.on('_disconnected', () => {
            setIsConnected(false);
            addLog('⚠️ Disconnected from event stream');
        });

        // Handle all events for logging
        const unsubAll = eventStream.on('*', (event: any) => {
            let level: LogObject['level'] = 'info';
            if (event.type.includes('error') || event.type.includes('failed')) level = 'error';
            if (event.type.includes('success') || event.type.includes('completed')) level = 'success';
            if (event.type.includes('warning')) level = 'warn';

            addLog(
                `${event.type.replace(/\./g, ' ').toUpperCase()}`,
                level,
                (event.source || 'MCP').toUpperCase()
            );
        });

        // Handle threat events
        const unsubThreat = eventStream.on('threat.detected', (event: any) => {
            addLog(`THREAT DETECTED: ${event.data?.type || 'Anomaly'}`, 'error', 'THREAT_ENGINE');
            const newThreat: Threat = {
                id: `TH-${Date.now().toString(36).slice(-4).toUpperCase()}`,
                severity: (event.data?.severity as 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL') || 'MEDIUM',
                type: (event.data?.type as Threat['type']) || 'Anomaly',
                timestamp: new Date().toLocaleTimeString(),
                status: 'DETECTED',
            };
            setThreats(prev => [newThreat, ...prev.slice(0, 9)]);
        });

        // Handle Real-Time Agent State Updates
        const unsubAgentState = eventStream.on('agent.lifecycle.*', (event: any) => {
            const { agent_id } = event.payload || event.data || {};
            if (!agent_id) return;

            let newState: AgentStatus = AgentStatus.IDLE;
            if (event.type.includes('resumed') || event.type.includes('spawned')) newState = AgentStatus.IDLE;
            if (event.type.includes('running')) newState = AgentStatus.RUNNING;
            if (event.type.includes('paused')) newState = AgentStatus.PAUSED;
            if (event.type.includes('terminated')) newState = AgentStatus.TERMINATED;

            setAgents(prev => prev.map(a =>
                a.id === agent_id ? { ...a, status: newState } : a
            ));
            addLog(`🔄 Agent ${agent_id} is now ${newState}`, 'info', 'ORCHESTRATOR');
        });

        // Handle agent status changes
        const unsubEthics = eventStream.on('ethics.validation.completed', (event: any) => {
            addLog(`⚖️ Ethics: ${event.data?.decision_type || 'completed'}`);
        });

        const unsubOsint = eventStream.on('osint.investigation.completed', (event: any) => {
            addLog(`🔍 OSINT: Investigation completed`);
        });

        const unsubMaxReconnect = eventStream.on('_max_reconnect', () => {
            setError('Connection lost. Please refresh the page.');
            addLog('❌ Max reconnection attempts reached');
        });

        // Cleanup
        return () => {
            unsubConnect();
            unsubDisconnect();
            unsubAll();
            unsubThreat();
            unsubAgentState();
            unsubEthics();
            unsubOsint();
            unsubMaxReconnect();
            // Do not disconnect singleton stream
        };
    }, [addLog]);

    // Initial fetch
    useEffect(() => {
        fetchAgents();
    }, [fetchAgents]);

    return {
        agents,
        threats,
        logs,
        isLoading,
        isConnected,
        error,
        refetch: fetchAgents,
    };
}
