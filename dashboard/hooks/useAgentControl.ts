
import { useState, useCallback, useEffect } from 'react';
import { Job } from '../types/agent';
import { eventStream } from '../services/eventStream';

export type AgentState = 'IDLE' | 'SPAWNED' | 'RUNNING' | 'PAUSED' | 'TERMINATED' | 'ERROR';

export function useAgentControl(agentId: string) {
    const [state, setState] = useState<AgentState>('IDLE');
    const [isLoading, setIsLoading] = useState(false);

    const performAction = useCallback(async (action: 'PAUSE' | 'RESUME' | 'CANCEL' | 'TERMINATE') => {
        setIsLoading(true);
        try {
            const response = await fetch(`/api/v1/agents/${agentId}/control`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });

            if (!response.ok) {
                throw new Error(`Failed to ${action} agent`);
            }

            // Wait for WebSocket event to update state naturally
            // or fetch status immediately if needed.
            // For now, we trust the EventStream subscription below.

        } catch (error) {
            console.error('C2 Control Error:', error);
            // Revert state or show error?
        } finally {
            setIsLoading(false);
        }
    }, [agentId]);

    // Subscribe to real-time state changes
    useEffect(() => {
        const { eventStream } = require('../services/eventStream'); // Import inside effect or top level

        const unsub = eventStream.on('agent.lifecycle.*', (event: any) => {
            const { agent_id } = event.payload || event.data || {};
            if (agent_id !== agentId) return;

            let newState: AgentState = 'IDLE';
            if (event.type.includes('resumed') || event.type.includes('spawned')) newState = 'IDLE'; // Pending RUNNING map
            if (event.type.includes('running')) newState = 'RUNNING';
            if (event.type.includes('paused')) newState = 'PAUSED';
            if (event.type.includes('terminated')) newState = 'TERMINATED';

            setState(newState);
        });

        return () => unsub();
    }, [agentId]);

    return {
        state,
        isLoading,
        pause: () => performAction('PAUSE'),
        resume: () => performAction('RESUME'),
        terminate: () => performAction('TERMINATE')
    };
}
