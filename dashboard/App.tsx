import React, { useState, useEffect, useMemo } from 'react';
import { NeuralNetwork } from './components/NeuralNetwork';
import {
  ThreatFeed, AgentList, GenAIConsole,
  ComplianceRadar, NetworkGraph
} from './components/DashboardWidgets';
import { ErrorBoundary } from './components/ErrorBoundary';
import { AgentSidebar, Agent } from './components/AgentSidebar';
import { AgentWorkspace } from './components/AgentWorkspace';
import { EthicalMagistratePanel } from './components/agents/EthicalMagistratePanel';
import { OSINTHunterPanel } from './components/agents/OSINTHunterPanel';
import { ThreatProphetPanel } from './components/agents/ThreatProphetPanel';
import { ComplianceGuardianPanel } from './components/agents/ComplianceGuardianPanel';
import { WargameExecutorPanel } from './components/agents/WargameExecutorPanel';
import { PatchValidatorPanel } from './components/agents/PatchValidatorPanel';
import { CyberSecAgentPanel } from './components/agents/CyberSecAgentPanel';
import { VisionarySentinelPanel } from './components/agents/VisionarySentinelPanel';
import { LiveLogTerminal, LogEntry } from './components/LiveLogTerminal';
import { mcpClient } from './services/mcpClient';

// OPTIMIZATION: Memoize the 3D Component. 
const MemoizedNeuralNetwork = React.memo(NeuralNetwork);

const App: React.FC = () => {
  const {
    agents: mcpAgents,
    threats,
    logs: mcpLogs,
    isLoading,
    isConnected,
    error,
    refetch
  } = useMCPAgents();

  const isOnline = useOnlineStatus();
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ethical-magistrate');
  const [showTerminal, setShowTerminal] = useState(true);
  const [activeModel, setActiveModel] = useState<'pro' | 'flash'>('pro');
  const [isSwitchingModel, setIsSwitchingModel] = useState(false);
  const [latencyPoints, setLatencyPoints] = useState<number[]>([20, 40, 15, 30, 45, 30, 25, 40]);

  // Simulação de pulso de latência (em prod viria do mcpClient)
  useEffect(() => {
    const interval = setInterval(() => {
      setLatencyPoints(prev => [...prev.slice(1), Math.floor(Math.random() * 30) + 15]);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Troca de modelo de IA
  const handleModelChange = async (alias: 'pro' | 'flash') => {
    setIsSwitchingModel(true);
    const result = await mcpClient.execute('set_ai_model', { model_alias: alias });
    if (result.success) {
      setActiveModel(alias);
    }
    setIsSwitchingModel(false);
  };

  // Mapeamento de agentes para o Sidebar (unificando dados do MCP com UI)
  const uiAgents: Agent[] = [
    { id: 'ethical-magistrate', name: 'Ethical Magistrate', icon: 'shield', status: 'active', statusMessage: 'Governance Core Active' },
    { id: 'osint-hunter', name: 'OSINT Hunter', icon: 'network', status: 'idle', statusMessage: 'Passive Recon Mode' },
    { id: 'threat-prophet', name: 'Threat Prophet', icon: 'activity', status: 'idle', statusMessage: 'Monitoring Feeds' },
    { id: 'compliance-guardian', name: 'Compliance Guardian', icon: 'lock', status: 'active', statusMessage: 'Frameworks Loaded' },
    { id: 'cybersec-agent', name: 'CyberSec Investigator', icon: 'terminal', status: 'idle', statusMessage: 'Security Recon' },
    { id: 'patch-validator', name: 'Patch Validator ML', icon: 'database', status: 'idle', statusMessage: 'ML Models Active' },
    { id: 'visionary-sentinel', name: 'Visionary Sentinel', icon: 'activity', status: 'active', statusMessage: 'Multimodal Neural Scan' },
    { id: 'wargame-executor', name: 'Wargame Executor', icon: 'terminal', status: 'idle', statusMessage: 'Scenarios Ready' },
  ];

  const selectedAgent = uiAgents.find(a => a.id === selectedAgentId) || uiAgents[0];

  return (
    <ErrorBoundary>
      <div className="w-full h-screen bg-background-dark text-slate-300 relative font-display select-none flex flex-col overflow-hidden">
        
        {/* Connection Status Toast */}
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
           {(!isConnected || error) && (
              <div className="bg-status-error/20 backdrop-blur-md border border-status-error/50 px-4 py-2 rounded-lg flex items-center gap-3 shadow-lg">
                <WifiOff className="w-4 h-4 text-status-error" />
                <span className="text-sm text-status-error font-bold">MCP DISCONNECTED</span>
                <button onClick={refetch} className="p-1 hover:bg-white/10 rounded transition-colors">
                  <RefreshCw className="w-3 h-3 text-white" />
                </button>
              </div>
           )}
        </div>

        {/* --- TOP NAVIGATION / HEADER --- */}
        <header className="h-20 shrink-0 border-b border-white/5 flex items-center justify-between px-8 bg-black/20 backdrop-blur-2xl z-20">
          <div className="flex items-center gap-6">
            <div className="relative group cursor-pointer">
              <div className="absolute inset-0 bg-primary blur-2xl opacity-20 group-hover:opacity-40 transition-opacity" />
              <Shield className="text-primary w-9 h-9 relative z-10 transition-transform group-hover:scale-105 duration-500" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-widest text-white flex items-center gap-2">
                VERTICE <span className="text-primary drop-shadow-neon-cyan">CYBER</span>
                <span className="text-[10px] py-0.5 px-1.5 rounded bg-primary/10 text-primary/70 border border-primary/20 ml-2 font-mono">v2.4.0</span>
              </h1>
              <div className="flex items-center gap-2 text-[9px] font-bold text-slate-600 uppercase tracking-[0.2em] mt-1">
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-status-online shadow-glow-status' : 'bg-status-warning animate-pulse'}`} />
                {isConnected ? 'Neural Link Established' : 'Connecting to Core...'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-10">
            {/* Quick Metrics */}
            <div className="hidden lg:flex items-center gap-8 border-r border-white/10 pr-10">
              <div className="flex items-center gap-4">
                 <Activity className="text-status-error w-4 h-4 opacity-70" />
                 <div>
                    <span className="block text-[8px] text-slate-500 uppercase font-black tracking-widest">Global Risk</span>
                    <span className="text-xs font-mono text-status-error font-bold">ELEVATED</span>
                 </div>
              </div>
              <div className="flex items-center gap-4">
                 <div className="flex flex-col items-end">
                    <span className="text-[8px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">AI Latency</span>
                    <svg className="w-16 h-6 text-secondary opacity-50" viewBox="0 0 100 40">
                      <path
                        d={`M 0 20 ${latencyPoints.map((p, i) => `L ${i * 14} ${40 - p}`).join(' ')}`}
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        className="heartbeat-line"
                      />
                    </svg>
                 </div>
                 <div className="h-8 w-px bg-white/5 mx-2" />
                 <div className="flex flex-col">
                    <span className="block text-[8px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">Logic Engine</span>
                    <div className="flex gap-1">
                      <button 
                        onClick={() => handleModelChange('pro')}
                        disabled={isSwitchingModel}
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded transition-all duration-300 ${activeModel === 'pro' ? 'bg-secondary text-white shadow-neon-purple scale-105' : 'bg-white/5 text-slate-500 hover:text-slate-300'}`}
                      >
                        3.0 PRO
                      </button>
                      <button 
                        onClick={() => handleModelChange('flash')}
                        disabled={isSwitchingModel}
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded transition-all duration-300 ${activeModel === 'flash' ? 'bg-primary text-background-dark shadow-neon-cyan scale-105' : 'bg-white/5 text-slate-500 hover:text-slate-300'}`}
                      >
                        3.0 FLASH
                      </button>
                    </div>
                 </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button className="p-2.5 rounded-xl bg-white/5 border border-white/5 hover:border-primary/30 transition-all group">
                 <Terminal className="w-5 h-5 text-slate-500 group-hover:text-primary transition-colors" />
              </button>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-900 border border-white/10 flex items-center justify-center text-xs font-bold text-slate-400">
                JD
              </div>
            </div>
          </div>
        </header>

        {/* --- MAIN LAYOUT --- */}
        <div className="flex-1 flex overflow-hidden p-6 gap-6">
          
          {/* Sidebar - Agent Selection */}
          <aside className="w-80 shrink-0 h-full">
            <AgentSidebar 
              agents={uiAgents}
              selectedAgentId={selectedAgentId}
              onSelectAgent={setSelectedAgentId}
            />
          </aside>

          {/* Center Column - Main Workspace */}
          <main className="flex-1 h-full flex flex-col gap-6">
            <div className="flex-1">
              <AgentWorkspace 
                agentName={selectedAgent.name}
                agentStatus={selectedAgent.status.toUpperCase()}
                description={selectedAgent.statusMessage}
              >
                {selectedAgentId === 'ethical-magistrate' && <EthicalMagistratePanel />}
                {selectedAgentId === 'osint-hunter' && <OSINTHunterPanel />}
                {selectedAgentId === 'threat-prophet' && <ThreatProphetPanel />}
                {selectedAgentId === 'compliance-guardian' && <ComplianceGuardianPanel />}
                {selectedAgentId === 'wargame-executor' && <WargameExecutorPanel />}
                {selectedAgentId === 'patch-validator' && <PatchValidatorPanel />}
                {selectedAgentId === 'cybersec-agent' && <CyberSecAgentPanel />}
                {selectedAgentId === 'visionary-sentinel' && <VisionarySentinelPanel />}
              </AgentWorkspace>
            </div>

            {/* Bottom Terminal */}
            {showTerminal && (
              <div className="h-64 shrink-0">
                <LiveLogTerminal 
                  logs={mcpLogs}
                  onClear={() => {}} 
                />
              </div>
            )}
          </main>

          {/* Right Column - Secondary Intelligence */}
          <aside className="w-80 shrink-0 h-full flex flex-col gap-4">
            <div className="h-1/2 overflow-hidden">
               <ThreatFeed threats={threats} />
            </div>
            <div className="flex-1 overflow-hidden">
               <AgentList agents={mcpAgents} />
            </div>
          </aside>

        </div>

        {/* Neural Background Overlay */}
        <div className="absolute inset-0 pointer-events-none z-0 opacity-10">
           <MemoizedNeuralNetwork agents={mcpAgents} />
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default App;
