import React from 'react';
import { Zap, GitCompare, SearchCheck } from 'lucide-react';

export default function ModeSelector({ mode, setMode }) {
  const modes = [
    {
      id: 'quick',
      title: 'Quick Mode',
      desc: 'Single LLM baseline response',
      icon: Zap,
      badge: 'Fastest',
    },
    {
      id: 'verify',
      title: 'Verify Mode',
      desc: 'Multi-LLM agreement & claim discrepancy detection',
      icon: GitCompare,
      badge: 'Cross-Check',
    },
    {
      id: 'deep',
      title: 'Deep Research',
      desc: 'Multi-LLM + Web Evidence + Claim Verification + Grounded Synthesis',
      icon: SearchCheck,
      badge: 'Full Verification',
    },
  ];

  return (
    <div className="space-y-2">
      <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
        Verification Depth
      </label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {modes.map((m) => {
          const Icon = m.icon;
          const isActive = mode === m.id;
          return (
            <div
              key={m.id}
              onClick={() => setMode(m.id)}
              className={`cursor-pointer rounded-lg border p-3.5 transition-all select-none relative overflow-hidden ${
                isActive
                  ? 'bg-slate-900 border-cyan-500/80 shadow-md shadow-cyan-950/30 ring-1 ring-cyan-500/40'
                  : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/40'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <div
                    className={`p-1.5 rounded-md ${
                      isActive ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className={`text-sm font-semibold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                    {m.title}
                  </span>
                </div>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                    isActive
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-800/80'
                      : 'bg-slate-800/80 text-slate-400'
                  }`}
                >
                  {m.badge}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">{m.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
