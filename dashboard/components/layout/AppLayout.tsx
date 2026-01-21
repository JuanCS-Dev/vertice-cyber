/**
 * App Layout
 * 
 * Defines the structural skeleton of the dashboard.
 * Consumes Contexts for global state (Connection, Selected Agent).
 * Decouples layout from logic.
 */

import React, { useState, Suspense } from 'react';
import { Shield, Activity, Terminal, WifiOff, RefreshCw } from 'lucide-react';
import { useTelemetry } from '../../contexts/TelemetryContext';
import { useAgentState } from '../../contexts/AgentStateContext';
import { AgentSidebar } from '../AgentSidebar';
import { AgentWorkspace } from '../AgentWorkspace';
import { LiveLogTerminal } from '../LiveLogTerminal';
import { ThreatFeed, AgentList } from '../DashboardWidgets';
import { ErrorBoundary } from '../ErrorBoundary';
import { mcpClient } from '../../services/mcpClient';

// Lazy load 3D background
const NeuralNetwork = React.lazy(() => import('../NeuralNetwork').then(m => ({ default: m.NeuralNetwork })));
const MemoizedNeuralNetwork = React.memo(NeuralNetwork);

interface AppLayoutProps {
  children?: React.ReactNode; // For future routing injection
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { isConnected, logBuffer } = useTelemetry();
  const { agents, threats, selectedAgentId, setSelectedAgentId } = useAgentState();
  
  const [showTerminal, setShowTerminal] = useState(true);
  const [activeModel, setActiveModel] = useState<'pro' | 'flash'>('pro');

  // Derived state
  const selectedAgent = agents.find(a => a.id === selectedAgentId) || agents[0];
  
  // Handlers
  const handleModelChange = async (alias: 'pro' | 'flash') => {
    setActiveModel(alias);
    await mcpClient.execute('set_ai_model', { model_alias: alias });
  };

  const handleReconnect = () => {
    window.location.reload(); // Simplest hard reconnect for now
  };

  // Convert LogBuffer to Array for Terminal (Virtualization handles performance)
  // In a real optimized scenario, LiveLogTerminal would subscribe directly to LogBuffer
  // But passing via props is acceptable for now if Terminal is optimized.
  // Actually, let's refactor LiveLogTerminal to accept the buffer directly later.
  // For this step, we'll do a simple state sync in a wrapper or just pass the snapshot.
  // To avoid re-renders here, we should ideally NOT pass logs as props if they update 100x/sec.
  // *Self-Correction*: The LiveLogTerminal component currently takes `logs` prop. 
  // We will leave it as is for this file, but we'll create a `ConnectedTerminal` wrapper later.
  
  // Temporary: We are not subscribing to logs here to avoid re-rendering layout!
  // The terminal should be self-contained. 
  
  return (
    <div className="w-full h-screen bg-background-dark text-slate-300 relative font-display select-none flex flex-col overflow-hidden">
        
        {/* --- HEADER --- */}
        <header className="h-20 shrink-0 border-b border-white/5 flex items-center justify-between px-8 bg-black/20 backdrop-blur-2xl z-20">
          {/* Brand */}
          <div className="flex items-center gap-6">
            <div className="relative group cursor-pointer">
              <div className="absolute inset-0 bg-primary blur-2xl opacity-20 group-hover:opacity-40 transition-opacity" />
              <Shield className="text-primary w-9 h-9 relative z-10 transition-transform group-hover:scale-105 duration-500" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-widest text-white flex items-center gap-2">
                VERTICE <span className="text-primary drop-shadow-neon-cyan">CYBER</span>
                <span className="text-[10px] py-0.5 px-1.5 rounded bg-primary/10 text-primary/70 border border-primary/20 ml-2 font-mono">v3.0.0</span>
              </h1>
              <div className="flex items-center gap-2 text-[9px] font-bold text-slate-600 uppercase tracking-[0.2em] mt-1">
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-status-online shadow-glow-status' : 'bg-status-warning animate-pulse'}`} />
                {isConnected ? 'Neural Link Established' : 'Connecting to Core...'}
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-10">
             {/* Latency / Model Switcher */}
             <div className="hidden lg:flex items-center gap-8 border-r border-white/10 pr-10">
                <div className="flex flex-col">
                  <span className="block text-[8px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">Logic Engine</span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleModelChange('pro')}
                      className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded transition-all duration-300 ${activeModel === 'pro' ? 'bg-secondary text-white shadow-neon-purple scale-105' : 'bg-white/5 text-slate-500 hover:text-slate-300'}`}
                    >
                      3.0 PRO
                    </button>
                    <button
                      onClick={() => handleModelChange('flash')}
                      className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded transition-all duration-300 ${activeModel === 'flash' ? 'bg-primary text-background-dark shadow-neon-cyan scale-105' : 'bg-white/5 text-slate-500 hover:text-slate-300'}`}
                    >
                      3.0 FLASH
                    </button>
                  </div>
                </div>
             </div>

             {/* User Profile */}
             <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-900 border border-white/10 flex items-center justify-center text-xs font-bold text-slate-400">
                JD
             </div>
          </div>
        </header>

        {/* --- MAIN CONTENT --- */}
        <div className="flex-1 flex overflow-hidden p-6 gap-6 z-10">
            {/* Left Sidebar */}
            <aside className="w-80 shrink-0 h-full">
                <AgentSidebar 
                    agents={agents}
                    selectedAgentId={selectedAgentId}
                    onSelectAgent={setSelectedAgentId}
                />
            </aside>

            {/* Center Workspace */}
            <main className="flex-1 h-full flex flex-col gap-6 min-w-0">
                <div className="flex-1 relative">
                    <ErrorBoundary>
                        <AgentWorkspace
                            agentName={selectedAgent?.name || 'Unknown'}
                            agentStatus={selectedAgent?.status?.toUpperCase() || 'OFFLINE'}
                            description={selectedAgent?.statusMessage || 'System unavailable'}
                        >
                            {children}
                        </AgentWorkspace>
                    </ErrorBoundary>
                </div>

                {/* Bottom Terminal */}
                {showTerminal && (
                    <div className="h-64 shrink-0">
                        <ConnectedTerminal />
                    </div>
                )}
            </main>

            {/* Right Sidebar */}
            <aside className="w-80 shrink-0 h-full flex flex-col gap-4">
                <div className="h-1/2 overflow-hidden">
                    <ThreatFeed threats={threats} />
                </div>
                <div className="flex-1 overflow-hidden">
                    <AgentList agents={agents} />
                </div>
            </aside>
        </div>

        {/* --- BACKGROUND --- */}
        <div className="absolute inset-0 pointer-events-none z-0 opacity-10">
            <Suspense fallback={null}>
                <MemoizedNeuralNetwork agents={agents} />
            </Suspense>
        </div>

        {/* --- TOASTS / ALERTS --- */}
        {(!isConnected) && (
            <div className="fixed top-24 right-8 z-50">
                <div className="bg-status-error/20 backdrop-blur-md border border-status-error/50 px-4 py-3 rounded-lg flex items-center gap-3 shadow-lg animate-in slide-in-from-right">
                    <WifiOff className="w-5 h-5 text-status-error" />
                    <div>
                        <p className="text-sm text-status-error font-bold">Connection Lost</p>
                        <p className="text-[10px] text-slate-300">Attempting to reconnect...</p>
                    </div>
                    <button onClick={handleReconnect} className="p-1 hover:bg-white/10 rounded transition-colors ml-2">
                        <RefreshCw className="w-4 h-4 text-white" />
                    </button>
                </div>
            </div>
        )}
    </div>
  );
};

// Internal Wrapper to connect Terminal to LogBuffer without re-rendering Layout
// This adheres to "Optimize the Hot Path"
import { useSyncExternalStore } from 'react';

const ConnectedTerminal: React.FC = () => {
    const { logBuffer } = useTelemetry();
    
    // Subscribe to buffer updates efficiently
    const logs = useSyncExternalStore(
        (cb) => logBuffer.subscribe(cb),
        () => logBuffer.getSnapshot(200) // Only get last 200 for UI
    );

    return (
        <LiveLogTerminal 
            logs={logs as any} // Cast needed due to type mismatch in legacy component vs new LogEntry
            onClear={() => logBuffer.clear()} 
        />
    );
};
