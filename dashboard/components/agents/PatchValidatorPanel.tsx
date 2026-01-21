import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Code, Loader2, AlertCircle, Cpu, FileDiff } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';

export const PatchValidatorPanel: React.FC = () => {
  const [diff, setDiff] = useState('');
  const [language, setLanguage] = useState('python');
  const [isValidating, setIsValidating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    if (!diff) return;
    setIsValidating(true);
    setError(null);
    setResult(null);
    
    const resp = await mcpClient.execute('patch_validate', {
      diff_content: diff,
      language: language
    });
    
    if (resp.success) {
      setResult(resp.data);
    } else {
      setError(resp.error || "Validation failed.");
    }
    setIsValidating(false);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Area (Left) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
              <FileDiff className="w-4 h-4" /> Patch Diff Analysis
            </h3>
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-black/40 border border-white/10 rounded px-2 py-1 text-[10px] text-slate-400 focus:outline-none"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
            </select>
          </div>
          
          <textarea
            value={diff}
            onChange={(e) => setDiff(e.target.value)}
            placeholder="Paste git diff or code patch here..."
            className="w-full h-96 bg-black/40 border border-white/10 rounded-xl p-4 font-mono text-[11px] text-slate-300 focus:outline-none focus:border-secondary/50 transition-all custom-scrollbar resize-none"
          />
          
          <button
            onClick={handleValidate}
            disabled={!diff || isValidating}
            className="w-full py-3 bg-secondary text-white font-bold rounded-lg hover:shadow-neon-purple transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isValidating ? <Loader2 className="w-5 h-5 animate-spin" /> : <ShieldCheck className="w-5 h-5" />}
            VALIDATE PATCH SECURITY
          </button>
        </div>

        {/* Results Area (Right) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {error && (
            <div className="bg-status-error/10 border border-status-error/20 rounded-lg p-4 text-status-error text-xs flex gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              {error}
            </div>
          )}

          {result ? (
            <div className="flex flex-col gap-4">
              <div className={`bg-black/20 rounded-xl border p-6 flex flex-col items-center text-center gap-4 transition-all duration-500 ${result.risk_score > 50 ? 'border-status-error shadow-[0_0_20px_rgba(239,68,68,0.1)]' : 'border-status-online shadow-[0_0_20px_rgba(34,197,94,0.1)]'}`}>
                 <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Security Risk Score</span>
                 <div className={`text-6xl font-bold ${result.risk_score > 50 ? 'text-status-error drop-shadow-neon-purple' : 'text-status-online'}`}>
                   {result.risk_score}
                 </div>
                 <span className={`px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest ${result.risk_score > 50 ? 'bg-status-error/20 text-status-error' : 'bg-status-online/20 text-status-online'}`}>
                   {result.risk_score > 50 ? 'UNSAFE PATCH' : 'SECURE PATCH'}
                 </span>
              </div>

              <div className="bg-black/20 rounded-xl border border-white/5 p-4 flex flex-col gap-4">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <Cpu className="w-3.5 h-3.5" /> Automated Analysis
                </h4>
                <div className="flex flex-col gap-2">
                  {result.findings?.map((f: any, i: number) => (
                    <div key={i} className="p-3 bg-white/5 rounded border border-white/5 flex gap-3">
                      <ShieldAlert className={`w-4 h-4 shrink-0 mt-0.5 ${f.severity === 'high' ? 'text-status-error' : 'text-status-warning'}`} />
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold text-white uppercase">{f.type}</span>
                          <span className="text-[8px] font-mono text-slate-500">{f.line ? `LINE ${f.line}` : ''}</span>
                        </div>
                        <p className="text-[10px] text-slate-400 leading-relaxed">{f.message}</p>
                      </div>
                    </div>
                  ))}
                  {(!result.findings || result.findings.length === 0) && (
                    <div className="flex items-center gap-3 p-3 text-status-online">
                      <ShieldCheck className="w-5 h-5" />
                      <span className="text-xs font-medium">No immediate vulnerabilities detected.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : !isValidating && (
            <div className="flex-1 flex flex-col items-center justify-center py-20 text-slate-700 gap-4 border-2 border-dashed border-white/5 rounded-xl">
              <Code className="w-16 h-16 opacity-20" />
              <p className="text-sm font-medium opacity-40">Ready for patch inspection</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
