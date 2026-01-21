import React from 'react';
import { Shield, Network, Database, Lock, Terminal, Activity, Cpu, HardDrive } from 'lucide-react';

export interface Agent {
  id: string;
  name: string;
  icon: string;
  status: 'active' | 'idle' | 'warning' | 'offline';
  statusMessage: string;
}

interface AgentSidebarProps {
  agents: Agent[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
  systemLoad?: { cpu: number; memory: string; disk: number };
}

const IconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  shield: Shield,
  network: Network,
  database: Database,
  lock: Lock,
  terminal: Terminal,
  activity: Activity,
};

export const AgentSidebar: React.FC<AgentSidebarProps> = ({
  agents,
  selectedAgentId,
  onSelectAgent,
  systemLoad = { cpu: 24, memory: "4.2GB", disk: 15 }
}) => {
  return (
    <div className="flex flex-col h-full glass-panel rounded-lg overflow-hidden border-border-dark">
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/5 bg-white/[0.02]">
        <h2 className="text-[10px] font-black tracking-widest text-slate-500 uppercase">
          Neural Core <span className="text-primary/50 ml-1">//</span> Agents
        </h2>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto py-3 custom-scrollbar">
        {agents.map((agent) => {
          const Icon = IconMap[agent.icon] || Terminal;
          const isSelected = agent.id === selectedAgentId;
          
          return (
            <button
              key={agent.id}
              onClick={() => onSelectAgent(agent.id)}
              className={`w-full px-5 py-3.5 flex items-center gap-4 transition-all duration-300 group relative ${
                isSelected ? 'active-agent-glow bg-primary/5' : 'hover:bg-white/[0.03]'
              }`}
            >
              <div className="relative shrink-0">
                <div className={`p-2 rounded-lg transition-colors ${isSelected ? 'bg-primary/10' : 'bg-white/5 group-hover:bg-white/10'}`}>
                  <Icon className={`w-4 h-4 ${isSelected ? 'text-primary' : 'text-slate-500 group-hover:text-slate-300'}`} />
                </div>
                <span className={`absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full border-2 border-background-card ${
                  agent.status === 'active' ? 'bg-status-online shadow-glow-status' :
                  agent.status === 'idle' ? 'bg-slate-600' :
                  agent.status === 'warning' ? 'bg-status-warning' : 'bg-status-error'
                }`} />
              </div>
              
              <div className="flex flex-col items-start overflow-hidden leading-tight">
                <span className={`text-xs font-bold transition-colors ${isSelected ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`}>
                  {agent.name}
                </span>
                <span className="text-[9px] text-slate-600 font-medium uppercase tracking-tight mt-0.5">
                  {agent.statusMessage}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* System Load Footer */}
      <div className="p-4 border-t border-border-dark bg-black/20">
        <div className="flex flex-col gap-3">
          <div className="flex justify-between items-center text-[10px] text-slate-400">
            <div className="flex items-center gap-1">
              <Cpu className="w-3 h-3 text-secondary" />
              <span>CPU: {systemLoad.cpu}%</span>
            </div>
            <div className="flex items-center gap-1">
              <HardDrive className="w-3 h-3 text-primary" />
              <span>MEM: {systemLoad.memory}</span>
            </div>
          </div>
          
          <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-1000" 
              style={{ width: `${systemLoad.cpu}%` }}
            />
          </div>

          <div className="flex items-center gap-2 mt-1">
             <div className="flex-1 h-0.5 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-primary/40 animate-pulse" style={{ width: '60%' }} />
             </div>
             <span className="text-[8px] font-mono text-slate-600 tracking-tighter">NODE_V.04</span>
          </div>
        </div>
      </div>
    </div>
  );
};
