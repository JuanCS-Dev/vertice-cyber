import React from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid 
} from 'recharts';
import { AlertTriangle, ShieldCheck, Activity, Terminal, Cpu, Zap } from 'lucide-react';
import { GlassCard, Badge } from './UI';
import { Agent, Threat, NetworkMetric, ComplianceMetric, AgentStatus } from '../types';

// --- Threat Feed Widget ---
export const ThreatFeed: React.FC<{ threats: Threat[] }> = ({ threats }) => {
  return (
    <GlassCard title="Threat Vector" neonColor="danger" className="h-full">
      <div className="h-full flex flex-col">
        <div className="flex-1 overflow-y-auto min-h-0 pr-2 space-y-2 scrollbar-thin">
          {threats.map((threat) => (
            <div key={threat.id} className="flex items-center justify-between p-3 bg-white/5 rounded-[2px] border border-white/5 text-sm hover:bg-white/10 transition-colors group">
              <div className="flex items-center gap-3">
                <AlertTriangle size={16} className={`${threat.severity === 'HIGH' || threat.severity === 'CRITICAL' ? 'text-cyber-danger animate-pulse' : 'text-yellow-500'}`} />
                <div>
                  <div className="font-mono text-[10px] text-gray-500 mb-0.5">{threat.timestamp}</div>
                  <div className="font-bold text-gray-200 text-xs tracking-wide">{threat.type}</div>
                </div>
              </div>
              <Badge type={threat.severity === 'CRITICAL' ? 'error' : threat.severity === 'HIGH' ? 'warning' : 'neutral'}>
                {threat.severity}
              </Badge>
            </div>
          ))}
          {threats.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-600 space-y-2">
              <ShieldCheck size={32} className="opacity-20" />
              <div className="text-xs font-mono italic">Sector Clear</div>
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
};

// --- Agent List Widget ---
export const AgentList: React.FC<{ agents: Agent[] }> = ({ agents }) => {
  return (
    <GlassCard title="Meta-Agents" neonColor="primary" className="h-full">
      <div className="h-full flex flex-col">
        <div className="flex-1 overflow-y-auto min-h-0 pr-2 space-y-3 scrollbar-thin">
          {agents.map((agent) => (
            <div key={agent.id} className="group p-1">
              <div className="flex justify-between items-center mb-1.5">
                <span className="font-mono text-xs font-bold text-cyber-primary flex items-center gap-2">
                  <span className={`w-1 h-1 rounded-full ${agent.status === 'OFFLINE' ? 'bg-red-500' : 'bg-cyber-primary'}`} />
                  {agent.name}
                </span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded-[2px] uppercase font-bold tracking-tighter ${agent.status === 'ENGAGED' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-gray-800 text-gray-500'}`}>
                  {agent.role}
                </span>
              </div>
              
              {/* Health Bar */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1 bg-gray-800/50 rounded-full overflow-hidden backdrop-blur-sm border border-white/5">
                  <div 
                    className={`h-full transition-all duration-700 ease-out ${agent.health < 40 ? 'bg-cyber-danger shadow-[0_0_10px_#ff006e]' : 'bg-cyber-primary shadow-[0_0_10px_#00ff9f]'}`} 
                    style={{ width: `${agent.health}%` }}
                  />
                </div>
                <span className="text-[10px] font-mono text-gray-400 w-8 text-right tabular-nums">{Math.round(agent.health)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </GlassCard>
  );
};

// --- GenAI Console ---
export const GenAIConsole: React.FC<{ logs: string[] }> = ({ logs }) => {
  const bottomRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <GlassCard title="GEMINI 3 PRO // CORE" neonColor="gemini" className="h-full">
      <div className="flex flex-col h-full font-mono text-[11px] leading-relaxed">
        <div className="flex-1 overflow-hidden relative rounded bg-black/40 border border-white/5 p-3">
          <div className="absolute inset-0 overflow-y-auto p-2 space-y-1.5 scrollbar-thin">
            {logs.map((log, i) => (
              <div key={i} className="text-blue-200/90 break-words flex gap-2">
                <span className="text-gemini-core select-none">➜</span>
                <span className="opacity-90">{log}</span>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2 text-gemini-core/80 animate-pulse text-[10px] border-t border-white/5 pt-2">
          <Terminal size={12} />
          <span className="tracking-widest">NEURAL LINK ACTIVE // MODEL: GEMINI-3-PRO</span>
        </div>
      </div>
    </GlassCard>
  );
};

// --- Charts ---
export const ComplianceRadar: React.FC<{ data: ComplianceMetric[] }> = ({ data }) => {
  return (
    <GlassCard title="Security Compliance" neonColor="info" className="h-full">
      <div className="h-full w-full min-h-[150px] relative">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#1e293b" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 9, fontWeight: 600 }} />
            <Radar
              name="Current"
              dataKey="A"
              stroke="#00d4ff"
              strokeWidth={2}
              fill="#00d4ff"
              fillOpacity={0.15}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
};

export const NetworkGraph: React.FC<{ data: NetworkMetric[] }> = ({ data }) => {
  return (
    <GlassCard title="Net Traffic" neonColor="primary" className="h-full">
      <div className="h-full w-full min-h-[150px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00ff9f" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#00ff9f" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="2 4" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="time" hide />
            <YAxis hide domain={[0, 1000]} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#050508', borderColor: '#334155', borderRadius: '4px', fontSize: '12px' }}
              itemStyle={{ color: '#00ff9f' }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Area type="monotone" dataKey="inbound" stroke="#00ff9f" strokeWidth={2} fillOpacity={1} fill="url(#colorIn)" />
            <Area type="monotone" dataKey="outbound" stroke="#00d4ff" strokeWidth={1} fillOpacity={0} fill="transparent" strokeDasharray="3 3" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
};