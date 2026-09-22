import React from 'react';
import { CheckCircle2, Clock, ChevronRight } from 'lucide-react';

export default function PipelineStepper({ stages, totalDurationMs }) {
  if (!stages || stages.length === 0) return null;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-3">
      <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
        <span className="font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Verification Pipeline Telemetry
        </span>
        <div className="flex items-center space-x-1.5 font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/50">
          <Clock className="w-3 h-3" />
          <span>Total: {(totalDurationMs / 1000).toFixed(2)}s</span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {stages.map((stage, idx) => (
          <React.Fragment key={idx}>
            <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 text-xs shadow-sm">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <div className="flex flex-col">
                <span className="font-medium text-slate-200">{stage.stage}</span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {stage.duration_ms}ms · {stage.detail}
                </span>
              </div>
            </div>
            {idx < stages.length - 1 && (
              <ChevronRight className="w-3.5 h-3.5 text-slate-700 shrink-0 hidden sm:block" />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
