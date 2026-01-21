import React, { useState } from 'react';
import { Lock, FileCheck, AlertCircle, Search, Loader2, ClipboardList, Shield } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';

export const ComplianceGuardianPanel: React.FC = () => {
  const [target, setTarget] = useState('');
  const [framework, setFramework] = useState('gdpr');
  const [isAssessing, setIsAssessing] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const frameworks = [
    { id: 'gdpr', name: 'GDPR', region: 'EU' },
    { id: 'pci_dss', name: 'PCI-DSS', region: 'Global' },
    { id: 'hipaa', name: 'HIPAA', region: 'US' },
    { id: 'iso27001', name: 'ISO 27001', region: 'Global' },
    { id: 'lgpd', name: 'LGPD', region: 'BR' },
  ];

  const handleAssess = async () => {
    if (!target) return;
    setIsAssessing(true);
    setError(null);
    
    const result = await mcpClient.execute('compliance_assess', {
      target: target,
      framework: framework
    });
    
    if (result.success) {
      setReport(result.data);
    } else {
      setError(result.error || "Compliance assessment failed.");
    }
    setIsAssessing(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Configuration Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 px-1">Framework</label>
          <select 
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-primary/50"
          >
            {frameworks.map(f => (
              <option key={f.id} value={f.id}>{f.name} ({f.region})</option>
            ))}
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 px-1">Assessment Target</label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="Cloud Asset, DB or System ID..."
                className="w-full bg-black/40 border border-white/10 rounded-lg py-2.5 pl-10 text-sm text-white focus:outline-none focus:border-primary/50"
              />
            </div>
            <button
              onClick={handleAssess}
              disabled={!target || isAssessing}
              className="px-6 py-2.5 bg-primary text-background-dark font-bold rounded-lg hover:shadow-neon-cyan transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {isAssessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
              ASSESS
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-status-error/10 border border-status-error/20 rounded-lg p-3 text-status-error text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {report ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Report */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            <div className="bg-black/20 rounded-xl border border-white/5 overflow-hidden">
              <div className="px-4 py-3 border-b border-white/5 bg-white/5 flex justify-between items-center">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                  <ClipboardList className="w-4 h-4 text-primary" /> Audit Findings
                </h3>
                <span className="text-[10px] font-mono text-slate-500">REF: {report.assessment_id}</span>
              </div>
              <div className="divide-y divide-white/5">
                {report.findings?.map((f: any, i: number) => (
                  <div key={i} className="p-4 hover:bg-white/5 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] border ${f.status === 'compliant' ? 'text-status-online border-status-online/20 bg-status-online/10' : 'text-status-error border-status-error/20 bg-status-error/10'}`}>
                          {f.status.toUpperCase()}
                        </span>
                        <span className="text-sm font-bold text-white">{f.requirement}</span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-500">{f.id}</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed ml-12">{f.description}</p>
                    {f.remediation && (
                      <div className="mt-3 ml-12 p-3 bg-primary/5 rounded border border-primary/10 flex gap-3">
                        <AlertCircle className="w-4 h-4 text-primary shrink-0" />
                        <div className="text-[10px] text-slate-300 leading-relaxed italic">
                          <span className="font-bold text-primary mr-1">Remediation:</span> {f.remediation}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Compliance Stats */}
          <div className="flex flex-col gap-4">
            <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 flex flex-col items-center text-center gap-4">
               <span className="text-[10px] font-bold text-primary uppercase tracking-widest">Compliance Score</span>
               <div className="text-5xl font-bold text-white drop-shadow-neon-cyan">
                 {report.score}%
               </div>
               <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                 <div className="h-full bg-primary" style={{ width: `${report.score}%` }} />
               </div>
            </div>

            <div className="bg-black/20 border border-white/5 rounded-xl p-4 flex flex-col gap-4">
               <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Summary</h4>
               <div className="grid grid-cols-2 gap-2">
                  <div className="p-3 bg-black/40 rounded border border-white/5">
                    <span className="text-[8px] text-slate-500 font-bold uppercase block mb-1">Passed</span>
                    <span className="text-xl font-bold text-status-online">{report.summary?.passed || 0}</span>
                  </div>
                  <div className="p-3 bg-black/40 rounded border border-white/5">
                    <span className="text-[8px] text-slate-500 font-bold uppercase block mb-1">Failed</span>
                    <span className="text-xl font-bold text-status-error">{report.summary?.failed || 0}</span>
                  </div>
               </div>
               <div className="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5">
                  <FileCheck className="w-4 h-4 text-slate-400" />
                  <span className="text-[9px] text-slate-400 font-medium">Auto-generated audit report ready.</span>
               </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center py-20 text-slate-600 gap-4">
          <Lock className="w-16 h-16 opacity-20" />
          <p className="font-bold tracking-widest uppercase text-sm opacity-40">Awaiting Assessment Configuration</p>
        </div>
      )}
    </div>
  );
};
