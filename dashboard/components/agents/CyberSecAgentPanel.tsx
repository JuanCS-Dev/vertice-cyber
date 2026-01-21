import React, { useState } from 'react';
import { Search, Globe, Shield, Loader2, AlertCircle, Server, Activity, Cpu } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';

export const CyberSecAgentPanel: React.FC = () => {
  const [target, setTarget] = useState('');
  const [scanPorts, setScanPorts] = useState(true);
  const [scanWeb, setScanWeb] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRecon = async () => {
    if (!target) return;
    setIsScanning(true);
    setError(null);
    setResult(null);
    
    const resp = await mcpClient.execute('cybersec_recon', {
      target: target,
      scan_ports: scanPorts,
      scan_web: scanWeb
    });
    
    if (resp.success) {
      setResult(resp.data);
    } else {
      setError(resp.error || "Reconnaissance failed.");
    }
    setIsScanning(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Search Header */}
      <div className="bg-black/20 rounded-xl border border-white/5 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 px-1">Recon Target</label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="Domain or IP address..."
                className="w-full bg-black/40 border border-white/10 rounded-lg py-2.5 pl-10 text-sm text-white focus:outline-none focus:border-primary/50"
              />
            </div>
          </div>
          <div className="flex items-center gap-6 px-4">
            <div className="flex items-center gap-2">
              <input 
                type="checkbox" 
                id="scanPorts" 
                checked={scanPorts} 
                onChange={e => setScanPorts(e.target.checked)}
                className="w-4 h-4 rounded bg-black/40 border-white/10 text-primary focus:ring-0"
              />
              <label htmlFor="scanPorts" className="text-[10px] font-bold text-slate-400 uppercase">Ports</label>
            </div>
            <div className="flex items-center gap-2">
              <input 
                type="checkbox" 
                id="scanWeb" 
                checked={scanWeb} 
                onChange={e => setScanWeb(e.target.checked)}
                className="w-4 h-4 rounded bg-black/40 border-white/10 text-primary focus:ring-0"
              />
              <label htmlFor="scanWeb" className="text-[10px] font-bold text-slate-400 uppercase">Web</label>
            </div>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleRecon}
              disabled={!target || isScanning}
              className="w-full md:w-auto px-8 py-2.5 bg-primary text-background-dark font-bold rounded-lg hover:shadow-neon-cyan transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isScanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              EXECUTE RECON
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-status-error/10 border border-status-error/20 rounded-lg p-4 text-status-error text-xs flex gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          {error}
        </div>
      )}

      {result ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ports Column */}
          {scanPorts && (
            <div className="bg-black/20 rounded-xl border border-white/5 overflow-hidden">
              <div className="px-4 py-3 border-b border-white/5 bg-white/5 flex items-center gap-2">
                <Server className="w-4 h-4 text-primary" />
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Network Ports</h3>
              </div>
              <div className="p-4 flex flex-col gap-2">
                {result.ports?.map((p: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded border border-white/5">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-mono font-bold text-white">{p.port}</span>
                      <span className="text-[10px] font-bold text-slate-500 uppercase">{p.service}</span>
                    </div>
                    <span className="text-[10px] font-bold text-status-online px-2 py-0.5 rounded bg-status-online/10 border border-status-online/20 uppercase tracking-tighter">Open</span>
                  </div>
                ))}
                {(!result.ports || result.ports.length === 0) && (
                  <div className="text-center py-8 text-slate-600 italic text-xs">No open ports identified.</div>
                )}
              </div>
            </div>
          )}

          {/* Web Data Column */}
          {scanWeb && (
            <div className="bg-black/20 rounded-xl border border-white/5 overflow-hidden">
              <div className="px-4 py-3 border-b border-white/5 bg-white/5 flex items-center gap-2">
                <Globe className="w-4 h-4 text-secondary" />
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Web Headers & Info</h3>
              </div>
              <div className="p-4 flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-2">
                   <div className="p-3 bg-black/40 rounded border border-white/5">
                      <span className="text-[8px] text-slate-500 uppercase font-bold block mb-1">Server</span>
                      <span className="text-[10px] text-white font-mono truncate block">{result.web?.server || 'Unknown'}</span>
                   </div>
                   <div className="p-3 bg-black/40 rounded border border-white/5">
                      <span className="text-[8px] text-slate-500 uppercase font-bold block mb-1">Security Score</span>
                      <span className="text-[10px] text-primary font-mono block">{result.web?.security_score || '--'}/100</span>
                   </div>
                </div>
                <div>
                  <span className="text-[8px] text-slate-500 uppercase font-bold block mb-2 px-1">Raw Headers</span>
                  <div className="p-3 bg-black/60 rounded border border-white/5 font-mono text-[9px] text-slate-400 h-48 overflow-y-auto custom-scrollbar leading-relaxed">
                    {result.web?.headers ? Object.entries(result.web.headers).map(([k, v]) => (
                      <div key={k} className="mb-1">
                        <span className="text-slate-500">{k}:</span> <span className="text-slate-300">{v as string}</span>
                      </div>
                    )) : 'No headers captured.'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : !isScanning && (
        <div className="flex-1 flex flex-col items-center justify-center py-20 text-slate-700 gap-4">
          <Activity className="w-16 h-16 opacity-20" />
          <p className="text-sm font-medium opacity-40 uppercase tracking-widest">Awaiting Recon Instructions</p>
        </div>
      )}
    </div>
  );
};
