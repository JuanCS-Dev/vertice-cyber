import React from 'react';

interface AgentWorkspaceProps {
  agentName: string;
  agentStatus: string;
  description: string;
  children: React.ReactNode;
}

export const AgentWorkspace: React.FC<AgentWorkspaceProps> = ({
  agentName,
  agentStatus,
  description,
  children
}) => {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Workspace Header */}
      <div className="flex items-end justify-between mb-6 px-1">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tightest">
            {agentName}
          </h1>
          <p className="text-xs text-slate-500 font-medium uppercase tracking-widest mt-1 opacity-80">
            {description}
          </p>
        </div>
        
        <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-white/[0.03] border border-white/5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">
            {agentStatus}
          </span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 glass-panel rounded-2xl overflow-hidden flex flex-col relative">
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          {children}
        </div>
      </div>
    </div>
  );
};
