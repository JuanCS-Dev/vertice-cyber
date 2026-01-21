import React, { useState } from 'react';
import { Activity, ShieldAlert, TrendingUp, Search, Loader2, AlertTriangle, ExternalLink } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';
import { AgentControlCard } from './AgentControlCard';
import { LiveTerminal } from '../CommandCenter/LiveTerminal';

interface ThreatIndicator {
  indicator_type: string;
  value: string;
  confidence: number;
  tags: string[];
}

interface MITRETechnique {
  id: string;
  name: string;
  description: string;
  tactics: string[];
}

interface Prediction {
  predicted_threats: string[];
  risk_level: string;
  recommended_actions: string[];
}

export const ThreatProphetPanel: React.FC = () => {
  const [target, setTarget] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!target) return;
    setIsAnalyzing(true);
    setError(null);

    const result = await mcpClient.execute('threat_analyze', {
      target: target,
      include_predictions: true
    });

    if (result.success) {
      setAnalysis(result.data);
    } else {
      setError(result.error || "Threat analysis failed.");
    }
    setIsAnalyzing(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Search Header */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="Target System, Asset or Organization..."
            className="w-full bg-black/40 border border-white/10 rounded-lg py-2.5 pl-10 text-sm text-white focus:outline-none focus:border-secondary/50"
          />
        </div>
        <button
          onClick={handleAnalyze}
          disabled={!target || isAnalyzing}
          className="px-6 py-2.5 bg-secondary text-white font-bold rounded-lg hover:shadow-neon-purple transition-all disabled:opacity-50 flex items-center gap-2"
        >
          {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
          ANALYZE THREATS
        </button>
      </div>

      {error && (
        <div className="bg-status-error/10 border border-status-error/20 rounded-lg p-3 text-status-error text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}

      {analysis ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Indicators & Techniques */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            <section>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                <ShieldAlert className="w-3.5 h-3.5" /> Intelligence Correlation
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {analysis.indicators?.map((ind: ThreatIndicator, i: number) => (
                  <div key={i} className="bg-white/5 border border-white/5 rounded-lg p-3 group hover:border-secondary/30 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-bold text-secondary uppercase">{ind.indicator_type}</span>
                      <span className="text-[10px] font-mono text-slate-500">{(ind.confidence * 100).toFixed(0)}% CONF</span>
                    </div>
                    <p className="text-sm font-mono text-white mb-2 truncate">{ind.value}</p>
                    <div className="flex flex-wrap gap-1">
                      {ind.tags.map(t => (
                        <span key={t} className="text-[8px] px-1.5 py-0.5 rounded bg-black/40 text-slate-400 border border-white/5">{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                <ExternalLink className="w-3.5 h-3.5" /> MITRE ATT&CK Mapping
              </h3>
              <div className="flex flex-col gap-2">
                {analysis.techniques?.map((tech: MITRETechnique) => (
                  <div key={tech.id} className="bg-black/20 border border-white/5 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-bold text-white">{tech.name}</span>
                      <span className="text-[10px] font-mono text-primary">{tech.id}</span>
                    </div>
                    <p className="text-[10px] text-slate-500 line-clamp-1">{tech.description}</p>
                    <div className="flex gap-2 mt-2">
                      {tech.tactics.map(t => (
                        <span key={t} className="text-[8px] font-bold text-slate-400 uppercase tracking-tighter">{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Predictions & Risk */}
          <div className="flex flex-col gap-6">

            {/* C2 CARD */}
            <AgentControlCard
              agentId="threat_prophet"
              agentType="THREAT PROPHET"
            />

            <div className="bg-secondary/5 border border-secondary/20 rounded-xl p-6 flex flex-col items-center text-center gap-4">
              <span className="text-[10px] font-bold text-secondary uppercase tracking-widest">Calculated Risk Score</span>
              <div className="text-5xl font-bold text-white drop-shadow-neon-purple">
                {analysis.overall_risk_score.toFixed(0)}
              </div>
              <div className="px-3 py-1 rounded bg-secondary text-[10px] font-bold text-white uppercase tracking-widest">
                {analysis.overall_risk_score > 70 ? 'CRITICAL' : 'ELEVATED'}
              </div>
            </div>

            {/* NEURAL STREAM */}
            <div className="bg-primary/5 border border-primary/10 rounded-lg p-0 overflow-hidden flex flex-col h-[250px]">
              <div className="px-4 py-2 bg-black/20 border-b border-primary/10">
                <h4 className="text-[10px] font-bold text-primary uppercase tracking-widest">Neural Link: THREAT</h4>
              </div>
              <div className="flex-1 min-h-0">
                <LiveTerminal filter="threat_prophet" />
              </div>
            </div>

            <section className="bg-black/20 border border-white/5 rounded-xl p-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" /> Predictive Insights
              </h3>
              {analysis.predictions?.map((pred: Prediction, i: number) => (
                <div key={i} className="flex flex-col gap-4">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase block mb-2">Likely Threat Patterns</span>
                    <div className="flex flex-col gap-1">
                      {pred.predicted_threats.map(t => (
                        <div key={t} className="text-xs text-white flex items-center gap-2">
                          <div className="w-1 h-1 rounded-full bg-secondary" /> {t}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase block mb-2">Countermeasures</span>
                    <div className="flex flex-col gap-1.5">
                      {pred.recommended_actions.map(a => (
                        <div key={a} className="text-[10px] text-slate-400 leading-relaxed pl-3 border-l border-white/10">
                          {a}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </section>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center py-20 text-slate-600 gap-4">
          <ShieldAlert className="w-16 h-16 opacity-20" />
          <p className="font-bold tracking-widest uppercase text-sm opacity-40">Awaiting Target Selection</p>
        </div>
      )}
    </div>
  );
};
