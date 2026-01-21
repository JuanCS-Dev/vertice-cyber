
import React, { useEffect, useState } from 'react';
import { LiveTerminal } from './LiveTerminal';
import { AgentControlCard } from '../agents/AgentControlCard';
import { eventStream } from '../../services/eventStream';

interface AgentSnapshot {
    agent_id: string;
    agent_type: string;
    state: any;
    config: any;
    active_job?: any;
}

export const OrchestratorView: React.FC = () => {
    const [agents, setAgents] = useState<AgentSnapshot[]>([]);

    const fetchSnapshot = async () => {
        try {
            const res = await fetch('/api/v1/snapshot');
            const data = await res.json();
            setAgents(data.agents || []);
        } catch (e) {
            console.error("Failed to fetch snapshot", e);
        }
    };

    useEffect(() => {
        fetchSnapshot();
        const interval = setInterval(fetchSnapshot, 5000); // Polling fallback

        // Real-time update trigger
        const unsub = eventStream.subscribe('agent.lifecycle.*', () => {
            fetchSnapshot();
        });

        return () => {
            clearInterval(interval);
            unsub();
        };
    }, []);

    return (
        <div className="h-full w-full flex flex-col gap-4 p-4 text-white">
            <header className="flex justify-between items-center border-b border-white/10 pb-4">
                <div>
                    <h1 className="text-xl font-bold tracking-[0.2em] font-mono">NEURAL MESH // C2</h1>
                    <span className="text-xs text-slate-500">GOD MODE ACTIVE</span>
                </div>
                <div className="flex gap-4 text-xs font-mono">
                    <span className="text-emerald-500">NODES: {agents.length}</span>
                    <span className="text-blue-500">ACTIVE: {agents.filter(a => a.state === 'RUNNING').length}</span>
                </div>
            </header>

            <div className="grid grid-cols-12 gap-4 flex-1 min-h-0">
                {/* Agents Grid */}
                <div className="col-span-8 grid grid-cols-2 gap-4 content-start overflow-y-auto pr-2 custom-scrollbar">
                    {agents.map(agent => (
                        <AgentControlCard
                            key={agent.agent_id}
                            agentId={agent.agent_id}
                            agentType={agent.agent_type}
                            initialState={agent.state}
                        />
                    ))}

                    {agents.length === 0 && (
                        <div className="col-span-2 text-center py-10 text-slate-600 border border-dashed border-slate-700/50 rounded-xl">
                            NO ACTIVE OPERATIVES DEPLOYED
                        </div>
                    )}
                </div>

                {/* Terminal & Logs */}
                <div className="col-span-4 flex flex-col gap-4 h-full">
                    <div className="flex-1 min-h-[400px]">
                        <LiveTerminal />
                    </div>
                </div>
            </div>
        </div>
    );
};
