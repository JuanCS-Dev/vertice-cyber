/**
 * useMCPAgents Hook
 * Gerencia estado dos agents MCP com real-time updates via WebSocket
 */

import { useState, useEffect, useCallback } from 'react';
import { mcpClient } from '../services/mcpClient';
import { eventStream } from '../services/eventStream';
import type { Agent, AgentStatus, Threat } from '../types';
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

            // Health check first
            const health = await mcpClient.health();
            if (health.status !== 'healthy') {
                throw new Error('MCP server is not healthy');
            }

            // Fetch tools
            const toolsResponse = await mcpClient.listTools();
            const tools = toolsResponse.tools;

            // Group tools by agent
            const agentMap = new Map<string, any[]>();
            for (const tool of tools) {
                const agentName = tool.agent;
                if (!agentMap.has(agentName)) {
                    agentMap.set(agentName, []);
                }
                agentMap.get(agentName)!.push(tool);
            }

            // Generate positions using existing algorithm
            const generatedAgents = generateAgents(agentMap.size);

            // Merge MCP data with generated positions
            let index = 0;
            const mergedAgents: Agent[] = [];

            for (const [agentName, agentTools] of agentMap) {
                const category = agentTools[0]?.category || 'intelligence';
                const role = CATEGORY_TO_ROLE[category] || 'Analyst';
                const genAgent = generatedAgents[index] || generatedAgents[0];

                mergedAgents.push({
                    ...genAgent,
                    id: `AG-${100 + index}`,
                    name: agentName,
                    role,
                    status: 'IDLE' as AgentStatus,
                    health: 100,
                    cpuLoad: Math.floor(Math.random() * 30) + 10,
                });

                index++;
            }

            setAgents(mergedAgents);
            addLog(`✅ Loaded ${tools.length} tools from ${mergedAgents.length} agents`);

        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Failed to fetch agents';
            setError(errorMsg);
            addLog(`❌ Error: ${errorMsg}`);

            // Fallback to generated agents
            setAgents(generateAgents(12));
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
            unsubEthics();
            unsubOsint();
            unsubMaxReconnect();
            eventStream.disconnect();
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
