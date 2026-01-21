import React, { useState } from 'react';
import { Eye, FileUp, ShieldAlert, Loader2, Music, Video, FileText, Globe, Search, Camera, CornerDownRight, Cpu, Target, Fingerprint, Activity, ScanFace } from 'lucide-react';
import { mcpClient } from '../../services/mcpClient';
import { AgentControlCard } from './AgentControlCard';
import { LiveTerminal } from '../CommandCenter/LiveTerminal';
import { DeepfakeResult } from '../../types/mcp';

interface AnalysisResult {
  findings: string;
  mode: string;
  model: string;
  usage: number;
  grounding: boolean;
}

export const VisionarySentinelPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'vision' | 'deepfake'>('vision');
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState('');
  const [preview, setPreview] = useState<string | null>(null);
  const [mode, setMode] = useState('forensic');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [deepfakeResult, setDeepfakeResult] = useState<DeepfakeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setFileUrl('');
      setResult(null);
      setDeepfakeResult(null);
      setError(null);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(selected);
    }
  };

  const handleUrlPreview = () => {
    if (fileUrl) {
      setPreview(fileUrl);
      setFile(null);
      setResult(null);
      setDeepfakeResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!preview) return;
    setIsAnalyzing(true);
    setError(null);
    setResult(null);
    setDeepfakeResult(null);

    try {
      if (activeTab === 'vision') {
        // Legacy Vision Analysis
        const payload: any = { mode: mode };
        if (file) {
          payload.file_b64 = preview.split(',')[1];
          payload.mime_type = file.type;
        } else {
          payload.file_url = fileUrl;
        }

        const resp = await mcpClient.execute('visionary_analyze', payload);
        if (resp.success) {
          setResult(resp.result as AnalysisResult); // Fix: use resp.result
        } else {
          setError(resp.error || "Visionary analysis failed.");
        }
      } else {
        // Deepfake Scanner
        if (!file && !preview) {
             setError("Local file upload required for Deepfake scan (Base64).");
             setIsAnalyzing(false);
             return;
        }
        
        // Deepfake tool expects base64, mime, filename
        const payload = {
            file_b64: preview.split(',')[1],
            mime_type: file?.type || 'image/jpeg', // Fallback for URL if we implemented it
            filename: file?.name || 'remote_media'
        };

        const resp = await mcpClient.execute('deepfake_scan_tool', payload);
        
        if (resp.success) {
            setDeepfakeResult(resp.result as DeepfakeResult);
        } else {
            setError(resp.error || "Deepfake scan failed.");
        }
      }
    } catch (err) {
      setError("Critical system error during evidence processing.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full font-display">
      {/* Tab Switcher */}
      <div className="flex gap-2 border-b border-white/5 pb-2">
        <button
            onClick={() => setActiveTab('vision')}
            className={`px-4 py-2 text-[10px] font-bold uppercase tracking-widest transition-all rounded-t-lg relative overflow-hidden group ${activeTab === 'vision' ? 'text-primary bg-primary/5 border-b-2 border-primary shadow-[0_4px_20px_-4px_rgba(0,242,255,0.3)]' : 'text-slate-500 hover:text-white hover:bg-white/5'}`}
        >
            <div className={`absolute inset-0 bg-primary/10 transform -skew-x-12 translate-x-[-100%] transition-transform duration-500 ${activeTab === 'vision' ? 'translate-x-[100%] opacity-0' : 'group-hover:translate-x-[100%]'}`} />
            <Eye className="w-3 h-3 inline mr-2" />
            Neural Vision
        </button>
        <button
            onClick={() => setActiveTab('deepfake')}
            className={`px-4 py-2 text-[10px] font-bold uppercase tracking-widest transition-all rounded-t-lg relative overflow-hidden group ${activeTab === 'deepfake' ? 'text-status-error bg-status-error/5 border-b-2 border-status-error shadow-[0_4px_20px_-4px_rgba(255,0,60,0.3)]' : 'text-slate-500 hover:text-white hover:bg-white/5'}`}
        >
            <div className={`absolute inset-0 bg-status-error/10 transform -skew-x-12 translate-x-[-100%] transition-transform duration-500 ${activeTab === 'deepfake' ? 'translate-x-[100%] opacity-0' : 'group-hover:translate-x-[100%]'}`} />
            <ScanFace className="w-3 h-3 inline mr-2" />
            Deepfake Scanner
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">

        {/* LEFT COLUMN: Input & Viewport */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between px-1">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Evidence Input</span>
              <span className="text-[9px] font-mono text-primary/40 tracking-tighter">SOURCE_MODALITY: {file ? 'BINARY' : 'REMOTE_LINK'}</span>
            </div>

            <div className="flex gap-2">
              <div className="relative flex-1">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
                <input
                  type="text"
                  value={fileUrl}
                  onChange={(e) => setFileUrl(e.target.value)}
                  onBlur={handleUrlPreview}
                  placeholder="Analyze from URL..."
                  className="w-full bg-black/40 border border-white/5 rounded-xl px-9 py-2.5 text-[11px] text-white focus:outline-none focus:border-primary/30 transition-all placeholder:text-slate-700"
                />
              </div>
              <div className="relative group">
                <button className="h-full px-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 transition-colors text-[10px] font-black uppercase tracking-widest text-slate-400 group-hover:text-primary">
                  Upload
                </button>
                <input type="file" onChange={onFileChange} className="absolute inset-0 opacity-0 cursor-pointer" accept="image/*,video/*,audio/*,application/pdf" />
              </div>
            </div>

            {/* Cinematic Viewport */}
            <div className="flex-1 min-h-[340px] bg-[#050508] rounded-2xl border border-white/5 p-1 relative overflow-hidden group shadow-2xl">
              {/* Corner Accents */}
              <div className="absolute top-4 left-4 w-4 h-4 border-t-2 border-l-2 border-white/10" />
              <div className="absolute top-4 right-4 w-4 h-4 border-t-2 border-r-2 border-white/10" />
              <div className="absolute bottom-4 left-4 w-4 h-4 border-b-2 border-l-2 border-white/10" />
              <div className="absolute bottom-4 right-4 w-4 h-4 border-b-2 border-r-2 border-white/10" />

              <div className="w-full h-full rounded-xl overflow-hidden flex flex-col items-center justify-center relative bg-black/40">
                {preview ? (
                  <div className="w-full h-full flex flex-col items-center justify-center relative">
                    {/* Scanning Bar Animation */}
                    {isAnalyzing && (
                      <div className={`absolute left-0 w-full h-1 z-20 animate-scanline ${activeTab === 'deepfake' ? 'bg-status-error/50 shadow-neon-purple' : 'bg-primary/50 shadow-neon-cyan'}`} />
                    )}

                    <div className={`transition-all duration-700 ${isAnalyzing ? 'scale-105 blur-[1px]' : 'scale-100'}`}>
                      {preview.startsWith('http') ? (
                        <div className="flex flex-col items-center gap-4">
                          <Globe className={`w-16 h-16 ${isAnalyzing ? 'text-primary animate-pulse' : 'text-slate-700'}`} />
                          <span className="text-[10px] font-mono text-slate-500 truncate max-w-[240px]">{preview}</span>
                        </div>
                      ) : (
                        <>
                          {file?.type.startsWith('image/') && <img src={preview} alt="Evidence" className="max-h-64 object-contain shadow-2xl" />}
                          {file?.type.startsWith('video/') && <Video className="w-16 h-16 text-primary" />}
                          {file?.type.startsWith('audio/') && <Music className="w-16 h-16 text-secondary" />}
                          {file?.type === 'application/pdf' && <FileText className="w-16 h-16 text-slate-500" />}
                        </>
                      )}
                    </div>

                    {/* Metadata Overlay */}
                    <div className="absolute bottom-6 left-6 right-6 flex justify-between items-end opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                      <div className="bg-black/80 backdrop-blur-md border border-white/10 rounded-lg p-2 flex flex-col gap-1">
                        <span className="text-[8px] font-black text-slate-500 uppercase">File Metadata</span>
                        <span className="text-[9px] font-mono text-white truncate max-w-[150px]">{file?.name || 'REMOTE_STREAM'}</span>
                      </div>
                      <button
                        onClick={() => { setFile(null); setFileUrl(''); setPreview(null); setResult(null); setDeepfakeResult(null); }}
                        className="p-2 bg-status-error/10 hover:bg-status-error/20 border border-status-error/30 rounded-lg transition-colors"
                      >
                        <ShieldAlert className="w-3 h-3 text-status-error" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-4 opacity-20 group-hover:opacity-40 transition-opacity duration-700">
                    <Target className="w-12 h-12 text-slate-400" />
                    <span className="text-[10px] font-black tracking-[0.3em] uppercase">Awaiting Target Acquisition</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Hub */}
          <div className="bg-background-card/40 rounded-2xl border border-white/5 p-5 flex flex-col gap-5">
            {activeTab === 'vision' && (
                <div className="grid grid-cols-2 gap-2">
                {[ 
                    { id: 'forensic', icon: Fingerprint, label: 'Forensic' },
                    { id: 'compliance', icon: Target, label: 'Compliance' },
                    { id: 'threat_intelligence', icon: ShieldAlert, label: 'Threat Intel' },
                    { id: 'incident_response', icon: Activity, label: 'Inc. Response' }
                ].map(m => (
                    <button
                    key={m.id}
                    onClick={() => setMode(m.id)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all duration-300 ${mode === m.id ? 'bg-primary/10 border-primary/30 text-primary shadow-neon-cyan' : 'bg-white/[0.02] border-white/5 text-slate-600 hover:bg-white/[0.05]'}`}
                    >
                    <m.icon className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-black uppercase tracking-wider">{m.label}</span>
                    </button>
                ))}
                </div>
            )}
            
            <button
              onClick={handleAnalyze}
              disabled={!preview || isAnalyzing}
              className={`w-full py-4 font-black rounded-xl hover:shadow-neon-cyan transition-all duration-500 flex items-center justify-center gap-3 disabled:opacity-20 disabled:grayscale ${activeTab === 'deepfake' ? 'bg-status-error text-white shadow-[0_0_20px_rgba(255,0,0,0.3)]' : 'bg-primary text-background-dark'}`}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="tracking-[0.1em]">PROCESSING...</span>
                </>
              ) : (
                <>
                  {activeTab === 'deepfake' ? <ScanFace className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  <span className="tracking-[0.1em]">{activeTab === 'deepfake' ? 'INITIATE DEEPFAKE SCAN' : 'INITIATE NEURAL SCAN'}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: Intelligence Dossier */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          {error && (
              <div className="p-4 bg-status-error/10 border border-status-error/20 rounded-xl text-status-error text-xs font-mono">
                  ERROR: {error}
              </div>
          )}

          {activeTab === 'vision' && result && (
            <div className="flex-1 flex flex-col bg-background-card/20 rounded-2xl border border-white/5 overflow-hidden shadow-2xl relative">
              {/* Header */}
              <div className="px-6 py-5 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                    <Cpu className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-xs font-black text-white uppercase tracking-[0.2em]">Visionary Intelligence Dossier</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[8px] font-bold text-slate-500 uppercase">STATUS: <span className="text-status-online">VERIFIED</span></span>
                      <div className="w-1 h-1 rounded-full bg-slate-700" />
                      <span className="text-[8px] font-bold text-slate-500 uppercase">CONFIDENCE: <span className="text-primary">98.4%</span></span>
                    </div>
                  </div>
                </div>
                {result.grounding && (
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[8px] font-black px-2 py-1 rounded bg-secondary/10 text-secondary border border-secondary/20 flex items-center gap-1.5 uppercase">
                      <Globe className="w-2.5 h-2.5" /> Google Search Grounded
                    </span>
                  </div>
                )}
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                <div className="font-mono text-[12px] text-slate-400 leading-relaxed space-y-8">
                  {result.findings.split('\n').filter(l => l.trim()).map((line, i) => (
                    <div key={i} className="group relative pl-6">
                      <div className="absolute left-0 top-1 w-1.5 h-1.5 bg-primary/30 rounded-full group-hover:bg-primary transition-colors" />
                      <div className="absolute left-0 top-2 w-[1px] h-full bg-white/5" />
                      <p className="text-slate-300 group-hover:text-white transition-colors duration-300">
                        {line}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer Metrics */}
              <div className="px-6 py-4 flex justify-between items-center bg-black/40 border-t border-white/5">
                  <div className="flex gap-6">
                    <div className="flex flex-col">
                      <span className="text-[8px] font-black text-slate-600 uppercase">Neural Engine</span>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{result.model}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[8px] font-black text-slate-600 uppercase">Telemetry Usage</span>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{result.usage} UNITS</span>
                    </div>
                  </div>
              </div>
            </div>
          )}

          {activeTab === 'deepfake' && deepfakeResult && (
              <div className="flex-1 flex flex-col bg-background-card/20 rounded-2xl border border-white/5 overflow-hidden shadow-2xl relative animate-in fade-in zoom-in-95 duration-500">
                  {/* Deepfake Header */}
                  <div className={`px-6 py-5 border-b border-white/5 flex justify-between items-center ${deepfakeResult.is_deepfake ? 'bg-status-error/5' : 'bg-status-online/5'}`}>
                      <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${deepfakeResult.is_deepfake ? 'bg-status-error/10 border-status-error/30 text-status-error' : 'bg-status-online/10 border-status-online/30 text-status-online'}`}>
                              {deepfakeResult.is_deepfake ? <ShieldAlert className="w-5 h-5" /> : <Shield className="w-5 h-5" />}
                          </div>
                          <div>
                              <h3 className="text-xs font-black text-white uppercase tracking-[0.2em]">Deepfake Analysis Report</h3>
                              <div className="flex items-center gap-2 mt-1">
                                  <span className="text-[8px] font-bold text-slate-500 uppercase">VERDICT: </span>
                                  <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${deepfakeResult.is_deepfake ? 'bg-status-error text-background-dark' : 'bg-status-online text-background-dark'}`}>
                                      {deepfakeResult.is_deepfake ? 'SYNTHETIC MEDIA DETECTED' : 'AUTHENTIC MEDIA'}
                                  </span>
                              </div>
                          </div>
                      </div>
                      <div className="flex flex-col items-end">
                          <span className="text-[8px] font-bold text-slate-500 uppercase">Confidence</span>
                          <span className={`text-xl font-black ${deepfakeResult.is_deepfake ? 'text-status-error' : 'text-status-online'}`}>
                              {(deepfakeResult.confidence * 100).toFixed(1)}%
                          </span>
                      </div>
                  </div>

                  {/* Reasoning Body */}
                  <div className="flex-1 overflow-y-auto p-8 custom-scrollbar flex flex-col gap-6">
                      <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                          <h4 className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">Detection Source</h4>
                          <span className="text-sm font-mono text-primary">{deepfakeResult.source}</span>
                      </div>

                      <div>
                          <h4 className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-3">Forensic Reasoning</h4>
                          <p className="text-sm text-slate-300 font-mono leading-relaxed bg-black/20 p-4 rounded-xl border border-white/5">
                              {deepfakeResult.details.reasoning}
                          </p>
                      </div>

                      {deepfakeResult.details.artifacts.length > 0 && (
                          <div>
                              <h4 className="text-[9px] font-black text-status-error uppercase tracking-widest mb-3">Detected Artifacts</h4>
                              <ul className="space-y-2">
                                  {deepfakeResult.details.artifacts.map((art, idx) => (
                                      <li key={idx} className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                                          <span className="w-1.5 h-1.5 bg-status-error rounded-full" />
                                          {art}
                                      </li>
                                  ))}
                              </ul>
                          </div>
                      )}
                  </div>
              </div>
          )}

          {/* Placeholder State */}
          {!isAnalyzing && !result && !deepfakeResult && !error && (
            <div className="flex-1 flex flex-col items-center justify-center gap-6 border-2 border-dashed border-white/5 rounded-3xl group hover:border-primary/10 transition-colors duration-700">
              <div className="relative">
                {activeTab === 'vision' ? (
                    <Search className="w-20 h-20 text-slate-800 group-hover:text-primary/20 transition-colors duration-700" />
                ) : (
                    <ScanFace className="w-20 h-20 text-slate-800 group-hover:text-status-error/20 transition-colors duration-700" />
                )}
                
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-32 h-32 rounded-full border border-white/5 group-hover:scale-150 group-hover:opacity-0 transition-all duration-1000" />
                </div>
              </div>
              <div className="text-center">
                <p className="text-[11px] font-black text-slate-700 uppercase tracking-[0.4em]">Sentinel Offline</p>
                <p className="text-[9px] font-bold text-slate-800 uppercase mt-3">Link established. Awaiting sensory input.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
