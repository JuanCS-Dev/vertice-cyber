import React, { useState, useEffect, useMemo } from 'react';
import { NeuralNetwork } from './components/NeuralNetwork';
import {
  ThreatFeed, AgentList, GenAIConsole,
  ComplianceRadar, NetworkGraph
} from './components/DashboardWidgets';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useMCPAgents } from './hooks/useMCPAgents';
import { useOnlineStatus } from './hooks/useOnlineStatus';
import { INITIAL_METRICS, Agent, NetworkMetric } from './types';
import { Shield, Zap, Activity, Cpu, Wifi, WifiOff, RefreshCw } from 'lucide-react';

// OPTIMIZATION: Memoize the 3D Component. 
const MemoizedNeuralNetwork = React.memo(NeuralNetwork);

// Connection Status Component
const ConnectionStatus: React.FC<{
  isLoading: boolean;
  isConnected: boolean;
  isOnline: boolean;
  error: string | null;
  onRetry: () => void;
}> = ({ isLoading, isConnected, isOnline, error, onRetry }) => {
  return (
    <div className="fixed top-20 right-4 z-50 flex flex-col gap-2 max-w-xs">
      {/* Offline Banner */}
      {!isOnline && (
        <div className="bg-red-500/20 backdrop-blur-sm border border-red-500/50 px-4 py-2 rounded-lg flex items-center gap-2 animate-pulse">
          <WifiOff className="w-4 h-4 text-red-400" />
          <span className="text-sm text-red-300">You are offline</span>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="bg-blue-500/20 backdrop-blur-sm border border-blue-500/50 px-4 py-2 rounded-lg flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          <span className="text-sm">Loading MCP agents...</span>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="bg-red-500/20 backdrop-blur-sm border border-red-500/50 px-4 py-2 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-red-300">⚠️ {error}</span>
          </div>
          <button
            onClick={onRetry}
            className="text-xs bg-red-500/30 hover:bg-red-500/50 px-3 py-1 rounded flex items-center gap-1 transition"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        </div>
      )}

      {/* WebSocket Disconnected */}
      {!isConnected && !isLoading && !error && isOnline && (
        <div className="bg-yellow-500/20 backdrop-blur-sm border border-yellow-500/50 px-4 py-2 rounded-lg flex items-center gap-2">
          <div className="w-2 h-2 bg-yellow-500 rounded-full" />
          <span className="text-sm text-yellow-300">WebSocket reconnecting...</span>
        </div>
      )}

      {/* Connected State */}
      {isConnected && !isLoading && !error && (
        <div className="bg-green-500/20 backdrop-blur-sm border border-green-500/50 px-4 py-2 rounded-lg flex items-center gap-2 opacity-80 hover:opacity-100 transition">
          <Wifi className="w-4 h-4 text-green-400" />
          <span className="text-sm text-green-300">MCP Connected</span>
        </div>
      )}
    </div>
  );
};

const App: React.FC = () => {
  // ========================================
  // MCP INTEGRATION (Real data, no mocks!)
  // ========================================
  const {
    agents,
    threats,
    logs,
    isLoading,
    isConnected,
    error,
    refetch
  } = useMCPAgents();

  const isOnline = useOnlineStatus();

  // Network data simulation (keep for now - could be replaced with real metrics later)
  const [networkData, setNetworkData] = useState<NetworkMetric[]>([]);

  // --- Initial Setup for Network Graph ---
  useEffect(() => {
    const initialNetData = Array.from({ length: 20 }).map((_, i) => ({
      time: i.toString(),
      inbound: Math.random() * 500 + 200,
      outbound: Math.random() * 300 + 100,
      latency: Math.random() * 20,
    }));
    setNetworkData(initialNetData);

    // Simulate network traffic (lightweight update)
    const interval = setInterval(() => {
      setNetworkData(prev => {
        const last = prev[prev.length - 1];
        return [...prev.slice(1), {
          time: new Date().toLocaleTimeString(),
          inbound: Math.max(100, Math.min(900, last.inbound + (Math.random() - 0.5) * 200)),
          outbound: Math.max(50, Math.min(600, last.outbound + (Math.random() - 0.5) * 100)),
          latency: Math.random() * 50
        }];
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Calculate active agents count
  const activeAgentCount = useMemo(() =>
    agents.filter(a => a.health > 0).length,
    [agents]
  );

  return (
    <ErrorBoundary>
      <div className="w-full min-h-screen lg:h-screen bg-background text-gray-200 relative font-sans select-none flex flex-col">

        {/* Background Effects (Fixed to viewport) */}
        <div className="scanline-bg pointer-events-none fixed inset-0 z-50" />
        <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900/50 via-[#050508] to-[#050508] pointer-events-none z-0" />

        {/* Connection Status Indicator */}
        <ConnectionStatus
          isLoading={isLoading}
          isConnected={isConnected}
          isOnline={isOnline}
          error={error}
          onRetry={refetch}
        />

        {/* --- HEADER --- */}
        <header className="h-16 shrink-0 border-b border-white/5 flex items-center justify-between px-4 md:px-6 bg-background/80 backdrop-blur-md relative z-20 shadow-[0_4px_30px_rgba(0,0,0,0.5)] sticky top-0 md:static">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Shield className="text-cyber-primary w-6 h-6 md:w-8 md:h-8 relative z-10" />
              <div className="absolute inset-0 bg-cyber-primary blur-md opacity-20" />
            </div>
            <div>
              <h1 className="font-tech text-lg md:text-2xl font-bold tracking-[0.2em] text-white leading-none">
                VERTICE <span className="text-cyber-primary drop-shadow-[0_0_5px_rgba(0,255,159,0.5)]">CYBER</span>
              </h1>
              <div className="flex items-center gap-2 text-[8px] md:text-[10px] text-cyber-info font-mono mt-0.5 opacity-70">
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-cyber-primary animate-pulse' : 'bg-yellow-500'}`} />
                {isConnected ? 'SYSTEM ONLINE // MCP CONNECTED' : 'CONNECTING TO MCP...'}
              </div>
            </div>
          </div>

          {/* Top KPI Metrics (Hidden on Mobile, Visible on LG+) */}
          <div className="hidden lg:flex items-center gap-12 border-l border-white/5 pl-8 h-10">
            <div className="flex items-center gap-3">
              <Activity className="text-cyber-danger" size={18} />
              <div>
                <div className="text-[9px] text-gray-500 uppercase tracking-widest">Threat Level</div>
                <div className="font-mono text-cyber-danger font-bold text-sm">
                  {threats.length > 5 ? 'HIGH' : threats.length > 2 ? 'MODERATE' : 'LOW'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Cpu className="text-gemini-core" size={18} />
              <div>
                <div className="text-[9px] text-gray-500 uppercase tracking-widest">MCP Status</div>
                <div className={`font-mono font-bold text-sm ${isConnected ? 'text-gemini-core' : 'text-yellow-500'}`}>
                  {isConnected ? 'ACTIVE' : 'CONNECTING'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Zap className="text-cyber-primary" size={18} />
              <div>
                <div className="text-[9px] text-gray-500 uppercase tracking-widest">Active Agents</div>
                <div className="font-mono text-cyber-primary font-bold text-sm">
                  {isLoading ? '...' : `${activeAgentCount}/${agents.length}`}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* --- MAIN LAYOUT --- */}
        <main className="flex-1 p-4 md:p-6 relative z-10 lg:overflow-hidden w-full">
          <div className="flex flex-col lg:grid lg:grid-cols-12 lg:grid-rows-1 gap-6 lg:h-full">

            {/* LEFT COLUMN */}
            <aside className="lg:col-span-3 flex flex-col gap-6 lg:h-full order-2 lg:order-1">
              <div className="h-64 lg:h-1/2">
                <ThreatFeed threats={threats} />
              </div>
              <div className="h-64 lg:h-1/2">
                <NetworkGraph data={networkData} />
              </div>
            </aside>

            {/* CENTER COLUMN (THE BRAIN) */}
            <section className="lg:col-span-6 relative rounded-sm border border-white/5 bg-black/40 overflow-hidden flex flex-col h-[400px] lg:h-auto lg:h-full order-1 lg:order-2">
              {/* 3D Scene Layer */}
              <div className="absolute inset-0 z-0">
                <MemoizedNeuralNetwork agents={agents} />
              </div>

              {/* Vignette Overlay for depth */}
              <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_40%,rgba(5,5,8,0.8)_100%)] z-0" />

              {/* Console Overlay at Bottom */}
              <div className="mt-auto z-10 h-1/3 w-full p-4 pointer-events-none">
                <div className="pointer-events-auto h-full">
                  <GenAIConsole logs={logs} />
                </div>
              </div>
            </section>

            {/* RIGHT COLUMN */}
            <aside className="lg:col-span-3 flex flex-col gap-6 lg:h-full order-3">
              <div className="h-64 lg:h-[40%]">
                <ComplianceRadar data={INITIAL_METRICS} />
              </div>
              <div className="h-80 lg:h-[60%]">
                <AgentList agents={agents} />
              </div>
            </aside>

          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
};

export default App;