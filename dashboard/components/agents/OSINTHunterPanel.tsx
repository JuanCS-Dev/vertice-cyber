import React, { useState } from 'react';
import { Search, Globe, Mail, Fingerprint, Loader2, Download, AlertTriangle, TrendingUp } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';
import { AgentControlCard } from './AgentControlCard';
import { LiveTerminal } from '../CommandCenter/LiveTerminal';

interface OSINTFinding {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  type: string;
  source: string;
  details: string;
  timestamp: string;
}

export const OSINTHunterPanel: React.FC = () => {
  const [target, setTarget] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [findings, setFindings] = useState<OSINTFinding[]>([]);
  const [riskScore, setRiskScore] = useState<number | null>(null);
  const [searchDepth, setSearchDepth] = useState<'basic' | 'deep' | 'exhaustive'>('basic');
  const [error, setError] = useState<string | null>(null);

  const isValidTarget = target.includes('.') || target.includes('@');

  const handleScan = async () => {
    if (!isValidTarget) return;
    setIsScanning(true);
    setError(null);
    setFindings([]);
    setRiskScore(null);

    const result = await mcpClient.execute('osint_investigate', {
      target: target,
      depth: searchDepth
    });

    if (result.success && result.data) {
      const data = result.data;

      // Converte findings do backend para o formato da UI
      const mappedFindings: OSINTFinding[] = (data.findings || []).map((f: any, idx: number) => ({
        id: `f-${idx}`,
        severity: f.severity || 'info',
        type: f.finding_type || 'General Intel',
        source: f.source || 'External',
        details: typeof f.data === 'string' ? f.data : JSON.stringify(f.data),
        timestamp: 'Just now'
      }));

      // Adiciona breaches se houver
      if (data.breaches && data.breaches.length > 0) {
        data.breaches.forEach((b: any, idx: number) => {
          mappedFindings.unshift({
            id: `b-${idx}`,
            severity: 'critical',
            type: 'Data Breach',
            source: 'HIBP',
            details: `${b.name} (${b.date}): ${b.data_classes.join(', ')}`,
            timestamp: 'Historical'
          });
        });
      }

      setFindings(mappedFindings);
      setRiskScore(data.risk_score || 0);
    } else {
      setError(result.error || "Investigation failed.");
    }

    setIsScanning(false);
  };

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'critical': return 'text-status-error bg-status-error/10 border-status-error/20';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-status-warning bg-status-warning/10 border-status-warning/20';
      case 'low': return 'text-status-online bg-status-online/10 border-status-online/20';
      default: return 'text-status-info bg-status-info/10 border-status-info/20';
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Target Acquisition */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="Enter Email, Domain or IP target..."
              className="w-full bg-black/40 border border-white/10 rounded-lg py-2.5 pl-10 pr-20 text-sm text-white focus:outline-none focus:border-primary/50 transition-all"
            />
            {target && (
              <div className={`absolute right-3 top-1/2 -translate-y-1/2 text-[9px] font-bold px-1.5 py-0.5 rounded ${isValidTarget ? 'bg-status-online/20 text-status-online' : 'bg-status-error/20 text-status-error'}`}>
                {isValidTarget ? 'VALID' : 'INVALID'}
              </div>
            )}
          </div>
          <button
            onClick={handleScan}
            disabled={!isValidTarget || isScanning}
            className="px-6 py-2.5 bg-primary text-background-dark font-bold rounded-lg hover:shadow-neon-cyan transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isScanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            INITIATE
          </button>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Depth:</span>
            {(['basic', 'deep', 'exhaustive'] as const).map((d) => (
              <button
                key={d}
                onClick={() => setSearchDepth(d)}
                className={`text-[10px] px-2 py-0.5 rounded border capitalize transition-colors ${searchDepth === d ? 'bg-primary/20 text-primary border-primary/20' : 'text-slate-500 border-white/5 hover:border-white/20'}`}
              >
                {d}
              </button>
            ))}
          </div>
          <div className="h-4 w-px bg-white/5" />
          <div className="flex items-center gap-4 text-slate-500">
            <Globe className="w-3.5 h-3.5 cursor-pointer hover:text-primary transition-colors" title="DNS Map" />
            <Mail className="w-3.5 h-3.5 cursor-pointer hover:text-primary transition-colors" title="Breach Check" />
            <Fingerprint className="w-3.5 h-3.5 cursor-pointer hover:text-primary transition-colors" title="Google Dorks" />
          </div>
        </div>

        {error && (
          <div className="bg-status-error/10 border border-status-error/20 rounded-lg p-3 flex items-center gap-3 text-status-error text-xs">
            <AlertTriangle className="w-4 h-4" />
            {error}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Results Table */}
        <div className="lg:col-span-3 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
              Intelligence Report {findings.length > 0 && <span className="text-primary font-mono">[{findings.length}]</span>}
            </h3>
            <button className="text-[10px] text-slate-500 hover:text-white flex items-center gap-1">
              <Download className="w-3 h-3" /> Export CSV
            </button>
          </div>

          <div className="bg-black/20 rounded-lg border border-white/5 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-white/5 text-slate-500 font-bold border-b border-white/5">
                  <th className="px-4 py-2 w-24">Severity</th>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2 w-24">Source</th>
                  <th className="px-4 py-2">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {findings.length > 0 ? findings.map(f => (
                  <tr key={f.id} className="hover:bg-white/5 transition-colors group">
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] border ${getSeverityColor(f.severity)}`}>
                        {f.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-white font-medium">{f.type}</td>
                    <td className="px-4 py-3 text-slate-400">{f.source}</td>
                    <td className="px-4 py-3 text-slate-500 group-hover:text-slate-300 transition-colors">{f.details}</td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-12 text-center text-slate-600 italic">
                      {isScanning ? 'Scan in progress...' : 'No data available. Initiate scan to gather intelligence.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Risk Gauge Sidebar */}
        <div className="flex flex-col gap-4">
          {/* ABSOLUTE CONTROL - C2 CARD */}
          <AgentControlCard
            agentId="osint_hunter"
            agentType="OSINT HUNTER"
          />

          <div className="bg-black/20 border border-white/5 rounded-lg p-6 flex flex-col items-center justify-center gap-4">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Target Risk Score</span>

            <div className="relative w-32 h-32">
              <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#1c2527" strokeWidth="8" />
                <circle
                  cx="50" cy="50" r="45" fill="none"
                  stroke={riskScore ? (riskScore > 75 ? '#ef4444' : '#eab308') : '#334155'}
                  strokeWidth="8"
                  strokeDasharray="282.7"
                  strokeDashoffset={riskScore ? 282.7 - (282.7 * riskScore / 100) : 282.7}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="flex items-center gap-1">
                  <span className="text-3xl font-bold text-white leading-none">{riskScore || '--'}</span>
                  {riskScore && (
                    <div className="flex flex-col text-[10px] text-status-error animate-bounce">
                      <TrendingUp className="w-3 h-3" />
                    </div>
                  )}
                </div>
                <span className={`text-[9px] font-bold mt-1 ${riskScore && riskScore > 75 ? 'text-status-error' : 'text-slate-500'}`}>
                  {riskScore ? (riskScore > 75 ? 'CRITICAL' : 'ELEVATED') : 'ANALYZING'}
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-1 w-full mt-2">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-500">Breaches</span>
                <span className="text-status-error font-mono">12</span>
              </div>
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-500">Social Profile</span>
                <span className="text-primary font-mono">4</span>
              </div>
            </div>
          </div>

          {/* LIVE NEURAL STREAM */}
          <div className="bg-primary/5 border border-primary/10 rounded-lg p-0 overflow-hidden flex flex-col h-[300px]">
            <div className="px-4 py-2 bg-black/20 border-b border-primary/10">
              <h4 className="text-[10px] font-bold text-primary uppercase tracking-widest">Neural Link: OSINT</h4>
            </div>
            <div className="flex-1 min-h-0">
              <LiveTerminal filter="osint" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
