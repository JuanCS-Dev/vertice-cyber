import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Loader2, History, AlertCircle } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';
import { AgentControlCard } from './AgentControlCard';
import { LiveTerminal } from '../CommandCenter/LiveTerminal';

interface MagistrateState {
  proposedAction: string;
  initiatingActor: 'auto' | 'admin' | 'api';
  piiRedactionEnabled: boolean;
  validationStatus: 'idle' | 'validating' | 'approved' | 'denied' | 'requires_review' | 'error';
  confidence: number | null;
  latency: number | null;
  reason: string | null;
  conditions: string[];
}

export const EthicalMagistratePanel: React.FC = () => {
  const [state, setState] = useState<MagistrateState>({
    proposedAction: '',
    initiatingActor: 'admin',
    piiRedactionEnabled: true,
    validationStatus: 'idle',
    confidence: null,
    latency: null,
    reason: null,
    conditions: []
  });

  const handleValidate = async () => {
    if (!state.proposedAction) return;

    setState(prev => ({ ...prev, validationStatus: 'validating', reason: null, conditions: [] }));

    const result = await mcpClient.execute('ethical_validate', {
      action: state.proposedAction,
      context: {
        has_pii: state.piiRedactionEnabled,
        actor_type: state.initiatingActor
      }
    });

    if (result.success && result.data) {
      const decision = result.data;
      let status: MagistrateState['validationStatus'] = 'denied';

      if (decision.is_approved) {
        status = 'approved';
      } else if (decision.decision_type === 'requires_human_review') {
        status = 'requires_review';
      }

      setState(prev => ({
        ...prev,
        validationStatus: status,
        confidence: decision.confidence || (decision.is_approved ? 95 : 40),
        latency: result.metadata.latencyMs,
        reason: decision.reasoning || "Decision processed by automated framework.",
        conditions: decision.conditions || []
      }));
    } else {
      setState(prev => ({
        ...prev,
        validationStatus: 'error',
        reason: result.error || "Failed to connect to Ethical Magistrate service.",
        latency: result.metadata.latencyMs
      }));
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      {/* Left Column: Input Form */}
      <div className="lg:col-span-2 flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">
            Proposed Counter-Measure
          </label>
          <textarea
            value={state.proposedAction}
            onChange={(e) => setState(prev => ({ ...prev, proposedAction: e.target.value }))}
            placeholder="e.g. ISOLATE_HOST(ip='192.168.1.45', duration='2h')"
            className="w-full h-48 bg-black/40 border border-white/10 rounded-lg p-4 font-mono text-sm text-primary focus:outline-none focus:border-primary/50 transition-colors resize-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Initiating Actor
            </label>
            <select
              value={state.initiatingActor}
              onChange={(e) => setState(prev => ({
                ...prev,
                initiatingActor: e.target.value as MagistrateState['initiatingActor']
              }))}
              className="bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-slate-300 focus:outline-none focus:border-primary/50"
            >
              <option value="admin">Administrator (Human)</option>
              <option value="auto">Autonomous Agent</option>
              <option value="api">External API Trigger</option>
            </select>
          </div>

          <div className="flex items-center gap-3 mt-6 px-2">
            <div
              onClick={() => setState(prev => ({ ...prev, piiRedactionEnabled: !prev.piiRedactionEnabled }))}
              className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${state.piiRedactionEnabled ? 'bg-primary' : 'bg-slate-700'}`}
            >
              <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${state.piiRedactionEnabled ? 'left-6' : 'left-1'}`} />
            </div>
            <span className="text-xs text-slate-400">Enforce PII Redaction</span>
          </div>
        </div>

        <button
          onClick={handleValidate}
          disabled={state.validationStatus === 'validating' || !state.proposedAction}
          className="mt-4 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-primary to-secondary text-white font-bold rounded-lg btn-neon disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {state.validationStatus === 'validating' ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <ShieldCheck className="w-5 h-5" />
          )}
          VALIDATE ACTION
        </button>
      </div>

      {/* Right Column: Validation Output */}
      <div className="flex flex-col gap-4">
        <div className="flex-1 bg-black/20 rounded-lg border border-white/5 p-5 flex flex-col items-center justify-center text-center gap-4">
          {state.validationStatus === 'idle' && (
            <>
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center">
                <History className="w-8 h-8 text-slate-600" />
              </div>
              <div>
                <h3 className="text-slate-400 font-bold">Awaiting Input</h3>
                <p className="text-[10px] text-slate-600 uppercase tracking-tighter mt-1">Ready for ethical audit</p>
              </div>
            </>
          )}

          {state.validationStatus === 'validating' && (
            <>
              <div className="w-16 h-16 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              <div className="animate-pulse">
                <h3 className="text-primary font-bold">Processing...</h3>
                <p className="text-[10px] text-primary/60 uppercase tracking-widest mt-1">Applying 7-Phase Framework</p>
              </div>
            </>
          )}

          {state.validationStatus === 'approved' && (
            <>
              <div className="w-16 h-16 rounded-full bg-status-online/20 flex items-center justify-center shadow-[0_0_20px_rgba(34,197,94,0.3)]">
                <ShieldCheck className="w-8 h-8 text-status-online" />
              </div>
              <div>
                <h3 className="text-status-online font-bold text-xl tracking-tight">APPROVED</h3>
                <div className="flex justify-center gap-1 mt-2">
                  {['POLICIES', 'FAIRNESS', 'SECURITY'].map(p => (
                    <span key={p} className="text-[7px] px-1.5 py-0.5 rounded-full bg-status-online/10 text-status-online/70 border border-status-online/20 font-black">
                      {p} CHECKED
                    </span>
                  ))}
                </div>
                <p className="text-[10px] text-slate-400 mt-3 px-4 italic leading-relaxed">
                  "{state.reason}"
                </p>
              </div>
            </>
          )}

          {state.validationStatus === 'denied' && (
            <>
              <div className="w-16 h-16 rounded-full bg-status-error/20 flex items-center justify-center shadow-[0_0_20px_rgba(239,68,68,0.3)]">
                <ShieldAlert className="w-8 h-8 text-status-error" />
              </div>
              <div>
                <h3 className="text-status-error font-bold text-xl tracking-tight">DENIED</h3>
                <p className="text-[10px] text-slate-400 mt-2 px-4 italic leading-relaxed">
                  "{state.reason}"
                </p>
              </div>
            </>
          )}

          {state.validationStatus === 'requires_review' && (
            <>
              <div className="w-16 h-16 rounded-full bg-status-warning/20 flex items-center justify-center shadow-[0_0_20px_rgba(234,179,8,0.3)]">
                <AlertCircle className="w-8 h-8 text-status-warning" />
              </div>
              <div>
                <h3 className="text-status-warning font-bold text-xl tracking-tight uppercase">Manual Review</h3>
                <p className="text-[10px] text-slate-400 mt-2 px-4 italic leading-relaxed">
                  "{state.reason}"
                </p>
              </div>
            </>
          )}

          {state.validationStatus === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-status-error" />
              </div>
              <div>
                <h3 className="text-status-error font-bold uppercase">System Error</h3>
                <p className="text-[10px] text-slate-500 mt-2 px-4">
                  {state.reason}
                </p>
              </div>
            </>
          )}
        </div>

        {/* Conditions List */}
        {state.conditions.length > 0 && (
          <div className="bg-primary/5 border border-primary/10 rounded p-3">
            <span className="block text-[8px] text-primary uppercase font-bold tracking-widest mb-2 text-center">Conditions for Approval</span>
            <ul className="flex flex-col gap-1.5">
              {state.conditions.map((c, i) => (
                <li key={i} className="text-[9px] text-slate-400 flex items-start gap-2">
                  <span className="text-primary mt-0.5">•</span>
                  {c}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Control & Neural Link */}
        <div className="flex flex-col gap-4">
          {/* C2 CARD */}
          <AgentControlCard
            agentId="magistrate"
            agentType="ETHICAL MAGISTRATE"
          />

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-black/20 border border-white/5 rounded p-3">
              <span className="block text-[8px] text-slate-500 uppercase font-bold tracking-widest">Confidence</span>
              <span className="text-lg font-mono text-white">
                {state.confidence ? `${state.confidence.toFixed(1)}%` : '--%'}
              </span>
            </div>
            <div className="bg-black/20 border border-white/5 rounded p-3">
              <span className="block text-[8px] text-slate-500 uppercase font-bold tracking-widest">Latency</span>
              <span className="text-lg font-mono text-white">
                {state.latency ? `${state.latency.toFixed(0)}ms` : '--ms'}
              </span>
            </div>
          </div>

          {/* LIVE NEURAL STREAM */}
          <div className="bg-primary/5 border border-primary/10 rounded-lg p-0 overflow-hidden flex flex-col h-[300px]">
            <div className="px-4 py-2 bg-black/20 border-b border-primary/10">
              <h4 className="text-[10px] font-bold text-primary uppercase tracking-widest">Neural Link: MAGISTRATE</h4>
            </div>
            <div className="flex-1 min-h-0">
              <LiveTerminal filter="magistrate" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
