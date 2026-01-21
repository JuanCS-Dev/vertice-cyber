import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2, Maximize2, Terminal as TerminalIcon } from 'lucide-react';

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success' | 'debug';
  source: string;
  message: string;
}

interface LiveLogTerminalProps {
  logs: LogEntry[];
  onClear?: () => void;
  onExpand?: () => void;
}

// Optimization: React.memo to prevent re-renders from parent state changes
export const LiveLogTerminal: React.FC<LiveLogTerminalProps> = React.memo(({
  logs,
  onClear,
  onExpand
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Optimization: Virtual Windowing (Simulated by slice)
  // Only render last 100 logs to DOM, keeping memory footprint O(1)
  const visibleLogs = logs.slice(-100);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]); // Dependency checks length/content

  const getLevelStyles = (level: string) => {
    switch (level) {
      case 'info': return 'text-primary';
      case 'warn': return 'text-status-warning';
      case 'error': return 'text-status-error';
      case 'success': return 'text-status-online';
      case 'debug': return 'text-slate-500';
      default: return 'text-slate-300';
    }
  };

  const getSourceStyles = (source: string) => {
    switch (source.toUpperCase()) {
      case 'SYSTEM': return 'text-slate-500';
      case 'MAGISTRATE': return 'text-secondary';
      case 'OSINT': return 'text-primary';
      case 'WARGAME': return 'text-status-error';
      case 'THREAT_ENGINE': return 'text-orange-400';
      case 'COMPLIANCE': return 'text-status-info';
      case 'AI_CORE': return 'text-secondary';
      default: return 'text-slate-400';
    }
  };

  const getSemanticEmoji = (level: string, source: string) => {
    if (level === 'error') return '❌';
    if (level === 'warn') return '⚠️';
    if (level === 'success') return '✅';

    switch (source.toUpperCase()) {
      case 'MAGISTRATE': return '⚖️';
      case 'OSINT': return '🔍';
      case 'THREAT_ENGINE': return '🔮';
      case 'COMPLIANCE': return '🛡️';
      case 'WARGAME': return '⚔️';
      case 'AI_CORE': return '🧠';
      case 'PATCH_VALIDATOR': return '🧬';
      case 'CYBERSEC': return '🛠️';
      case 'SYSTEM': return '⚙️';
      default: return '📡';
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/40 border border-white/5 rounded-2xl overflow-hidden font-mono">
      {/* Header */}
      <div className="px-5 py-3 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-3 text-slate-500">
          <TerminalIcon className="w-3.5 h-3.5" />
          <span className="text-[9px] font-black uppercase tracking-[0.2em] text-neon-green/80">
            Web Assembly Kernel v4.0
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-status-online animate-pulse shadow-glow-status" />
            <span className="text-[8px] font-bold text-slate-600 uppercase">Stream: {logs.length / 1000}k Ops/s</span>
          </div>
          <div className="h-3 w-px bg-white/10" />
          <button
            onClick={onClear}
            className="text-slate-600 hover:text-white transition-colors"
            title="Purge stream"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Logs Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-5 flex flex-col gap-2 custom-scrollbar bg-black/20 will-change-transform transform-gpu"
      >
        {visibleLogs.length > 0 ? visibleLogs.map((log, idx) => (
          <div key={idx} className="flex gap-4 leading-relaxed group text-[11px] font-light tracking-wide">
            <span className="text-slate-700 shrink-0 select-none">{(logs.length - visibleLogs.length + idx + 1).toString().padStart(4, '0')}</span>
            <span className="text-slate-600 shrink-0">[{log.timestamp}]</span>
            <span className="shrink-0">{getSemanticEmoji(log.level, log.source)}</span>
            <span className={`font-bold shrink-0 uppercase w-14 ${getLevelStyles(log.level)}`}>
              {log.level}
            </span>
            <span className={`shrink-0 font-bold ${getSourceStyles(log.source)}`}>
              {log.source}
            </span>
            <span className="text-slate-400 break-all group-hover:text-slate-200 transition-colors">
              {log.message}
            </span>
          </div>
        )) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-700 gap-2 opacity-50">
            <Terminal className="w-8 h-8" />
            <span className="italic">Awaiting agent activity...</span>
          </div>
        )}
        <div className="typing-cursor text-primary/40 h-4 mt-1" />
      </div>

      {/* Footer / Status */}
      <div className="px-4 py-1.5 border-t border-white/5 bg-black/20 text-[9px] text-slate-600 flex justify-between">
        <span>RENDERER: WEBGL_2.0</span>
        <span>VIRTUAL_BUFFER: {logs.length} / VISIBLE: {visibleLogs.length}</span>
      </div>
    </div>
  );
});
