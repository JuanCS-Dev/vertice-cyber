import React, { useState, useEffect } from 'react';
import { Terminal, ShieldAlert, Play, List, Loader2, AlertTriangle, Monitor, Activity } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';

export const WargameExecutorPanel: React.FC = () => {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenario, setSelectedAgentScenario] = useState<string | null>(null);
  const [target, setTarget] = useState('local');
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loadingScenarios, setLoadingScenarios] = useState(true);

  useEffect(() => {
    const fetchScenarios = async () => {
      const resp = await mcpClient.execute('wargame_list_scenarios');
      if (resp.success) {
        setScenarios(resp.data || []);
      }
      setLoadingScenarios(false);
    };
    fetchScenarios();
  }, []);

  const handleRun = async () => {
    if (!selectedScenario) return;
    setIsExecuting(true);
    setResult(null);
    
    const resp = await mcpClient.execute('wargame_run_simulation', {
      scenario_id: selectedScenario,
      target: target
    });
    
    if (resp.success) {
      setResult(resp.data);
    }
    setIsExecuting(false);
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        {/* Scenario Selection (Left) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="bg-black/20 rounded-xl border border-white/5 overflow-hidden flex flex-col h-full">
            <div className="px-4 py-3 border-b border-white/5 bg-white/5 flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <List className="w-4 h-4 text-primary" /> Attack Scenarios
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
              {loadingScenarios ? (
                <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-slate-700" /></div>
              ) : scenarios.map(s => (
                <button
                  key={s.id}
                  onClick={() => setSelectedAgentScenario(s.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-all mb-2 ${selectedScenario === s.id ? 'bg-primary/10 border-primary/30' : 'bg-transparent border-transparent hover:bg-white/5'}`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className={`text-xs font-bold ${selectedScenario === s.id ? 'text-primary' : 'text-slate-300'}`}>{s.name}</span>
                    <span className="text-[8px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-slate-500 uppercase">{s.difficulty}</span>
                  </div>
                  <p className="text-[10px] text-slate-500 line-clamp-2">{s.description}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Execution Console (Center/Right) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="bg-black/20 rounded-xl border border-white/5 p-4 flex flex-col gap-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 px-1">Simulation Target</label>
                <div className="relative">
                  <Monitor className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-lg py-2 pl-10 text-sm text-white focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleRun}
                  disabled={!selectedScenario || isExecuting}
                  className="w-full py-2.5 bg-status-error/80 text-white font-bold rounded-lg hover:bg-status-error transition-all shadow-[0_0_15px_rgba(239,68,68,0.2)] flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isExecuting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  INITIATE SIMULATION
                </button>
              </div>
            </div>
          </div>

          <div className="flex-1 bg-black/40 rounded-xl border border-white/5 font-mono text-[11px] overflow-hidden flex flex-col">
            <div className="px-4 py-2 border-b border-white/5 bg-black/40 flex justify-between items-center">
              <span className="text-slate-500 uppercase font-bold text-[9px] tracking-widest">Execution Log</span>
              {result && <span className="text-[9px] px-2 py-0.5 rounded bg-status-online/10 text-status-online border border-status-online/20 uppercase font-bold">COMPLETED</span>}
            </div>
            <div className="flex-1 overflow-y-auto p-4 custom-scrollbar flex flex-col gap-1.5">
              {isExecuting && (
                <div className="flex flex-col gap-1.5 animate-pulse">
                  <p className="text-slate-500">[SYSTEM] Provisioning sandbox environment...</p>
                  <p className="text-slate-500">[SYSTEM] Loading attack vectors...</p>
                  <p className="text-primary">[WARGAME] Initializing technique sequence...</p>
                </div>
              )}
              {result ? result.logs.map((log: string, i: number) => (
                <p key={i} className="text-slate-300 leading-relaxed">
                  <span className="text-slate-600">[{new Date().toLocaleTimeString()}]</span> {log}
                </p>
              )) : !isExecuting && (
                <div className="h-full flex flex-col items-center justify-center text-slate-700 opacity-50 italic">
                  <Terminal className="w-12 h-12 mb-2" />
                  Select a scenario and initiate to see execution logs
                </div>
              )}
            </div>
            
            {result && (
              <div className="p-4 border-t border-white/5 bg-black/40 grid grid-cols-3 gap-4">
                <div className="flex flex-col gap-1">
                  <span className="text-[8px] text-slate-500 uppercase font-bold">Detection Rate</span>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-status-online shadow-glow-status" style={{ width: `${result.detection_rate * 100}%` }} />
                    </div>
                    <span className="text-xs font-bold text-white">{(result.detection_rate * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <div className="flex flex-col gap-1 text-center">
                  <span className="text-[8px] text-slate-500 uppercase font-bold text-center">Success</span>
                  <span className={`text-xs font-bold ${result.success ? 'text-status-online' : 'text-status-error'}`}>
                    {result.success ? 'TRUE' : 'FALSE'}
                  </span>
                </div>
                <div className="flex flex-col gap-1 text-right">
                  <span className="text-[8px] text-slate-500 uppercase font-bold text-right">Artifacts</span>
                  <span className="text-[10px] text-primary underline cursor-pointer truncate">
                    {result.artifacts?.report_path?.split('/').pop() || 'report.json'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
