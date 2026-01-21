
import React from 'react';
import { Play, Pause, Square, Power } from 'lucide-react';
import { useAgentControl, AgentState } from '../../hooks/useAgentControl';
import { AgentConfig } from '../../types/agent';

interface AgentControlCardProps {
    agentId: string;
    agentType: string;
    initialState?: AgentState;
    config?: AgentConfig;
}

export const AgentControlCard: React.FC<AgentControlCardProps> = ({
    agentId,
    agentType,
    initialState = 'IDLE'
}) => {
    const { state, isLoading, pause, resume, terminate } = useAgentControl(agentId);

    // Use prop state if hook state is IDLE (initial load)
    const displayState = state === 'IDLE' && initialState !== 'IDLE' ? initialState : state;

    return (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col gap-4">
            <div className="flex justify-between items-center">
                <div>
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">{agentType}</h3>
                    <span className="text-xs text-slate-500 font-mono">{agentId}</span>
                </div>
                <StatusBadge state={displayState} />
            </div>

            <div className="flex gap-2 mt-2">
                {displayState === 'RUNNING' ? (
                    <button
                        onClick={pause}
                        disabled={isLoading}
                        className="flex-1 btn-control bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30"
                    >
                        <Pause className="w-4 h-4 mr-2" />
                        PAUSE
                    </button>
                ) : (
                    <button
                        onClick={resume}
                        disabled={isLoading || displayState === 'TERMINATED'}
                        className="flex-1 btn-control bg-emerald-500/20 text-emerald-500 hover:bg-emerald-500/30"
                    >
                        <Play className="w-4 h-4 mr-2" />
                        RESUME
                    </button>
                )}

                <button
                    onClick={() => terminate()} // Correct call
                    disabled={isLoading || displayState === 'TERMINATED'}
                    className="flex-none p-2 rounded-lg bg-red-500/20 text-red-500 hover:bg-red-500/30 transition-colors"
                >
                    <Power className="w-4 h-4" />
                </button>
            </div>

            {/* Queue Visualization - Removed until implemented with real data */}
        </div>
    );
};

const StatusBadge: React.FC<{ state: string }> = ({ state }) => {
    const styles = {
        IDLE: 'bg-slate-500/20 text-slate-400',
        SPAWNED: 'bg-blue-500/20 text-blue-400',
        RUNNING: 'bg-emerald-500/20 text-emerald-400 animate-pulse',
        PAUSED: 'bg-yellow-500/20 text-yellow-400',
        TERMINATED: 'bg-red-500/20 text-red-400',
        ERROR: 'bg-red-600/20 text-red-500'
    };

    return (
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${styles[state as keyof typeof styles] || styles.IDLE}`}>
            {state}
        </span>
    );
};
