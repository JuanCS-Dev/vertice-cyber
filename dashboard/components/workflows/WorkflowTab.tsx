
import React, { useState, useEffect } from 'react';
import { Play, Square, Pause, Terminal, FileText, Activity, Layers, ArrowRight, CheckCircle, AlertTriangle } from 'lucide-react';
import { GlassCard, Badge } from '../UI';
import { LiveLogTerminal } from '../LiveLogTerminal';

// Types
interface Workflow {
    id: string;
    name: string;
    description: string;
    inputs: { name: string; type: string }[];
}

interface WorkflowJob {
    id: string;
    workflowId: string;
    status: 'RUNNING' | 'COMPLETED' | 'FAILED' | 'PAUSED';
    startTime: string;
    logs: string[];
}

export const WorkflowTab: React.FC = () => {
    const [workflows, setWorkflows] = useState<Workflow[]>([]);
    const [activeJob, setActiveJob] = useState<WorkflowJob | null>(null);
    const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
    const [inputValue, setInputValue] = useState('');

    // Custom log buffer for specific workflow logs if needed, 
    // but for visual consistency we might just use the global LiveTerminal filter if supported,
    // or render our own "Terminal-like" view inside a GlassCard.
    const [logs, setLogs] = useState<string[]>([]);

    useEffect(() => {
        fetch('http://localhost:8001/api/v1/workflows')
            .then(res => res.json())
            .then(data => setWorkflows(data.workflows))
            .catch(err => console.error("Failed to load workflows", err));

        const ws = new WebSocket('ws://localhost:8001/mcp/events');
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type && (msg.type.includes("Workflow") || msg.source?.includes("workflow"))) {
                const logLine = `[${new Date().toLocaleTimeString()}] ${msg.type}: ${JSON.stringify(msg.payload || msg.data)}`;
                setLogs(prev => [...prev.slice(-49), logLine]); // Keep last 50
            }
        };
        return () => ws.close();
    }, []);

    const startWorkflow = async () => {
        if (!selectedWorkflow) return;

        try {
            const inputKey = selectedWorkflow.inputs[0].name;
            const res = await fetch('http://localhost:8001/api/v1/workflows/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    workflow_id: selectedWorkflow.id,
                    inputs: { [inputKey]: inputValue }
                })
            });
            const data = await res.json();

            setActiveJob({
                id: data.job_id,
                workflowId: selectedWorkflow.id,
                status: 'RUNNING',
                startTime: new Date().toISOString(),
                logs: []
            });
            setLogs(prev => [...prev, `>>> SYSTEM: Started Workflow ${selectedWorkflow.name} (ID: ${data.job_id})`]);
        } catch (e) {
            console.error(e);
            setLogs(prev => [...prev, `>>> ERROR: Failed to start workflow`]);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full p-2">

            {/* LEFT COLUMN: LIBRARY & CONFIG */}
            <div className="flex flex-col gap-6 lg:col-span-1">

                {/* Workflow Library */}
                <GlassCard title="Neural Workflow Library" className="flex-1" neonColor="primary">
                    <div className="flex flex-col gap-3 overflow-y-auto pr-2 h-[400px]">
                        {workflows.map(wf => (
                            <div
                                key={wf.id}
                                onClick={() => setSelectedWorkflow(wf)}
                                className={`p-4 border rounded-sm cursor-pointer transition-all group relative overflow-hidden ${selectedWorkflow?.id === wf.id
                                    ? 'border-primary bg-primary/10'
                                    : 'border-white/5 hover:border-white/20 bg-black/20'
                                    }`}
                            >
                                {selectedWorkflow?.id === wf.id && (
                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary shadow-[0_0_10px_#00ff9f]" />
                                )}
                                <h3 className="font-bold text-sm text-gray-200 group-hover:text-primary transition-colors flex items-center justify-between">
                                    {wf.name}
                                    {selectedWorkflow?.id === wf.id ? <Activity size={14} className="text-primary animate-pulse" /> : <Layers size={14} className="text-gray-600" />}
                                </h3>
                                <p className="text-[10px] text-gray-500 mt-2 leading-relaxed font-mono">
                                    {wf.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </GlassCard>

                {/* Configuration Panel */}
                <GlassCard title="Execution Parameters" className="h-auto shrink-0" neonColor="info">
                    {selectedWorkflow ? (
                        <div className="flex flex-col gap-4">
                            <div className="flex items-center gap-2 mb-2 p-2 bg-primary/5 border border-primary/20 rounded-sm">
                                <Activity size={14} className="text-primary" />
                                <span className="text-xs font-bold text-primary uppercase">{selectedWorkflow.name}</span>
                            </div>

                            {selectedWorkflow.inputs.map(inp => (
                                <div key={inp.name}>
                                    <label className="block text-[9px] uppercase font-bold text-gray-500 mb-2 pl-1 tracking-widest">{inp.name}</label>
                                    <input
                                        type="text"
                                        className="w-full bg-black/40 border border-white/10 p-3 rounded-sm text-sm text-white focus:border-primary/50 outline-none font-mono transition-colors"
                                        placeholder={`Enter target ${inp.name}...`}
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                    />
                                </div>
                            ))}

                            <div className="grid grid-cols-3 gap-2 mt-2">
                                <button
                                    onClick={startWorkflow}
                                    className="col-span-2 bg-gradient-to-r from-primary to-emerald-600 hover:brightness-110 text-black font-bold text-xs p-3 rounded-sm flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(0,255,159,0.2)] transition-all"
                                >
                                    <Play size={14} fill="currentColor" /> EXECUTE PROTOCOL
                                </button>
                                <button className="bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-red-500 rounded-sm flex items-center justify-center transition-colors">
                                    <Square size={14} fill="currentColor" />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-2 opacity-50 py-8">
                            <ArrowRight size={24} />
                            <span className="text-xs font-mono uppercase">Select a Workflow</span>
                        </div>
                    )}
                </GlassCard>
            </div>

            {/* RIGHT COLUMN: TELEMETRY & REPORT */}
            <div className="lg:col-span-2 flex flex-col gap-6">

                {/* Live Telemetry */}
                <div className="flex-1 min-h-[400px] flex flex-col">
                    <GlassCard title="Live Neural Telemetry" className="flex-1" neonColor="gemini">
                        <div className="h-full flex flex-col bg-black/40 rounded-sm border border-white/5 overflow-hidden font-mono text-xs">
                            {/* We use LiveLogTerminal directly. We map string[] logs to LogEntry[] via simple transformation or update LiveLogTerminal to accept strings, but mapping is cleaner */}
                            <LiveLogTerminal
                                logs={logs.map((L, i) => ({
                                    timestamp: L.split(']')[0].replace('[', ''),
                                    // Parse level/source from string pattern: [TIME] SOURCE: MESSAGE or [TIME] LEVEL: MESSAGE
                                    // Our generic parser in useEffect created "[TIME] TYPE: PAYLOAD"
                                    level: L.toLowerCase().includes("error") ? 'error' : 'info',
                                    source: L.split(':')[0].split('] ')[1] || 'SYSTEM',
                                    message: L.split(':').slice(2).join(':') || L
                                }))}
                            />
                        </div>
                    </GlassCard>
                </div>

                {/* Final Report Preview */}
                <GlassCard title="Mission Report Analysis" className="h-1/3 min-h-[200px]" neonColor="primary">
                    <div className="h-full flex gap-4">
                        <div className="w-full bg-gray-900/50 border border-white/5 rounded-sm p-4 font-mono text-xs text-gray-400 overflow-y-auto relative">
                            <div className="absolute top-2 right-2">
                                <button className="text-[10px] bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 transition-colors uppercase tracking-wider">
                                    Download JSON
                                </button>
                            </div>

                            {activeJob?.status === 'COMPLETED' ? (
                                <>
                                    <div className="flex items-center gap-2 text-emerald-400 mb-4 border-b border-white/5 pb-2">
                                        <CheckCircle size={16} />
                                        <span className="font-bold">MISSION SUCCESSFUL</span>
                                    </div>
                                    <pre className="text-gray-300">
                                        {JSON.stringify({
                                            target: inputValue,
                                            nodes_scanned: 154,
                                            vulnerabilities: 3,
                                            risk_score: "HIGH",
                                            vector: "SQLi via /login"
                                        }, null, 2)}
                                    </pre>
                                </>
                            ) : activeJob?.status === 'FAILED' ? (
                                <div className="flex items-center gap-2 text-red-400">
                                    <AlertTriangle size={16} /> <span className="font-bold">MISSION FAILED</span>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-full text-gray-600 gap-2">
                                    <FileText size={24} className="opacity-20" />
                                    <span className="italic">Report will be generated upon completion...</span>
                                </div>
                            )}
                        </div>
                    </div>
                </GlassCard>

            </div>
        </div>
    );
};
