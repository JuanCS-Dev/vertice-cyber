/**
 * Agent State Context
 * 
 * Manages the domain state: Agents list, Active Selection, Threats.
 * Decoupled from Telemetry/Logs.
 */

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { Agent, AgentStatus, Threat } from '../types';
import { useTelemetry } from './TelemetryContext';
import { eventStream } from '../services/eventStream';

interface AgentStateContextValue {
  agents: Agent[];
  threats: Threat[];
  selectedAgentId: string | null;
  setSelectedAgentId: (id: string | null) => void;
  isLoading: boolean;
  refreshAgents: () => Promise<void>;
}

const AgentStateContext = createContext<AgentStateContextValue | null>(null);

// Static UI Definitions (The "Ideal" State)
// We merge this with backend status
const UI_AGENTS_DEF: Partial<Agent>[] = [
    { id: 'ethical-magistrate', name: 'Ethical Magistrate', icon: 'shield', role: 'Guardian' },
    { id: 'osint-hunter', name: 'OSINT Hunter', icon: 'network', role: 'Hunter' },
    { id: 'threat-prophet', name: 'Threat Prophet', icon: 'activity', role: 'Analyst' },
    { id: 'compliance-guardian', name: 'Compliance Guardian', icon: 'lock', role: 'Guardian' },
    { id: 'cybersec-agent', name: 'CyberSec Investigator', icon: 'terminal', role: 'Hunter' },
    { id: 'patch-validator', name: 'Patch Validator ML', icon: 'database', role: 'Analyst' },
    { id: 'visionary-sentinel', name: 'Visionary Sentinel', icon: 'activity', role: 'Specialist' },
    { id: 'wargame-executor', name: 'Wargame Executor', icon: 'terminal', role: 'Hunter' },
    { id: 'workflows-manager', name: 'AI Workflows', icon: 'activity', role: 'Specialist' },
];

export const AgentStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { addLog } = useTelemetry();
  
  const [agents, setAgents] = useState<Agent[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ethical-magistrate');
  const [isLoading, setIsLoading] = useState(true);

  // Initialize Agents (Merge UI Def with default status)
  useEffect(() => {
    const initialAgents: Agent[] = UI_AGENTS_DEF.map(def => ({
      id: def.id!,
      name: def.name!,
      icon: def.icon!,
      role: def.role!,
      status: AgentStatus.IDLE,
      health: 100,
      cpuLoad: 0,
      memoryMB: 0,
      tasksCompleted: 0,
      position: [0,0,0], // Layout handled by NeuralNetwork or 3D Logic
      statusMessage: 'Initializing...'
    }));
    setAgents(initialAgents);
    setIsLoading(false);
  }, []);

  const refreshAgents = useCallback(async () => {
    // In a real scenario, fetch /api/agents/status and merge
    // For now, we rely on event stream updates for status
    // addLog('Refreshed agent status', 'info', 'ORCHESTRATOR');
  }, []);

  useEffect(() => {
    // Subscribe to Lifecycle Events
    const unsubLifecycle = eventStream.on('agent.lifecycle.*', (event: any) => {
      const { agent_id } = event.payload || event.data || {};
      if (!agent_id) return;

      let newState: AgentStatus = AgentStatus.IDLE;
      const type = event.type || '';
      
      if (type.includes('running')) newState = AgentStatus.RUNNING;
      else if (type.includes('paused')) newState = AgentStatus.PAUSED;
      else if (type.includes('terminated')) newState = AgentStatus.TERMINATED;
      else if (type.includes('error')) newState = AgentStatus.ERROR;

      setAgents(prev => prev.map(agent => {
        if (agent.id === agent_id) {
            return { 
                ...agent, 
                status: newState,
                statusMessage: event.message || agent.statusMessage
            };
        }
        return agent;
      }));
    });

    // Subscribe to Threat Events
    const unsubThreats = eventStream.on('threat.detected', (event: any) => {
        const newThreat: Threat = {
            id: `TH-${Date.now().toString(36).slice(-4).toUpperCase()}`,
            severity: event.data?.severity || 'MEDIUM',
            type: event.data?.type || 'Anomaly',
            timestamp: new Date().toLocaleTimeString(),
            status: 'DETECTED'
        };
        setThreats(prev => [newThreat, ...prev.slice(0, 49)]); // Keep last 50
    });

    return () => {
        unsubLifecycle();
        unsubThreats();
    };
  }, []);

  const value = useMemo(() => ({
    agents,
    threats,
    selectedAgentId,
    setSelectedAgentId,
    isLoading,
    refreshAgents
  }), [agents, threats, selectedAgentId, isLoading, refreshAgents]);

  return (
    <AgentStateContext.Provider value={value}>
      {children}
    </AgentStateContext.Provider>
  );
};

export const useAgentState = () => {
    const context = useContext(AgentStateContext);
    if (!context) throw new Error('useAgentState must be used within AgentStateProvider');
    return context;
};
