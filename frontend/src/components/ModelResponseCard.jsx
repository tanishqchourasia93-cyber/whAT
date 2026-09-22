import React, { useState } from 'react';
import { Bot, Clock, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function ModelResponseCard({ responses }) {
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (!responses || responses.length === 0) return null;

  const current = responses[selectedIdx] || responses[0];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden shadow-lg">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/80">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-semibold text-slate-200">Raw Model Outputs</span>
        </div>
        <div className="flex items-center space-x-1.5 overflow-x-auto">
          {responses.map((r, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedIdx(idx)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                selectedIdx === idx
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
            >
              {r.provider_name}
            </button>
          ))}
        </div>
      </div>

      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/60 pb-2">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-300">{current.provider_name}</span>
            <span className="font-mono text-slate-500 text-[11px]">({current.model_name})</span>
          </div>
          <div className="flex items-center space-x-3">
            <span className="flex items-center space-x-1 font-mono text-slate-400">
              <Clock className="w-3 h-3 text-slate-500" />
              <span>{current.latency_ms}ms</span>
            </span>
            {current.status === 'success' ? (
              <span className="flex items-center space-x-1 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3 h-3" />
                <span>Success</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-rose-400 font-medium">
                <AlertTriangle className="w-3 h-3" />
                <span>Failed</span>
              </span>
            )}
          </div>
        </div>

        {current.status === 'error' ? (
          <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300">
            {current.error || 'Failed to generate response'}
          </div>
        ) : (
          <div className="text-sm text-slate-300 leading-relaxed font-sans whitespace-pre-wrap max-h-60 overflow-y-auto pr-2">
            {current.content}
          </div>
        )}
      </div>
    </div>
  );
}
