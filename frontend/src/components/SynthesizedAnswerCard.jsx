import React from 'react';
import { Sparkles, ShieldCheck, AlertTriangle, CheckCircle, Info, Copy, Check } from 'lucide-react';

export default function SynthesizedAnswerCard({ answer, metrics, confidence, question }) {
  const [copied, setCopied] = React.useState(false);

  if (!answer) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getConfidenceBadge = (conf) => {
    switch (conf) {
      case 'HIGH CONFIDENCE':
        return {
          label: 'High System Confidence',
          desc: 'Consensus across models with authoritative external corroboration',
          color: 'bg-emerald-950/80 text-emerald-300 border-emerald-800',
          icon: ShieldCheck,
        };
      case 'MEDIUM CONFIDENCE':
        return {
          label: 'Medium System Confidence',
          desc: 'Evidence exists but partial discrepancies or limited sources detected',
          color: 'bg-cyan-950/80 text-cyan-300 border-cyan-800',
          icon: Info,
        };
      case 'LOW CONFIDENCE':
        return {
          label: 'Low System Confidence',
          desc: 'Active cross-model disagreements or contested evidence identified',
          color: 'bg-rose-950/80 text-rose-300 border-rose-800',
          icon: AlertTriangle,
        };
      default:
        return {
          label: 'Unverified Status',
          desc: 'Insufficient external evidence to establish validation',
          color: 'bg-slate-900 text-slate-400 border-slate-700',
          icon: Info,
        };
    }
  };

  const confBadge = getConfidenceBadge(metrics?.overall_confidence || confidence || 'MEDIUM CONFIDENCE');
  const ConfIcon = confBadge.icon;

  return (
    <div className="rounded-2xl border border-slate-700/80 bg-gradient-to-b from-slate-900 via-slate-900/95 to-slate-950 p-5 sm:p-6 shadow-xl space-y-4 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header with confidence & hallucination metric */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3.5">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800/80 flex items-center justify-center text-cyan-400 shadow-sm">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Evidence-Backed Synthesized Answer</h3>
            <span className="text-xs text-slate-400 font-mono">Cross-referenced against external records</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div
            title={confBadge.desc}
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border shadow-sm ${confBadge.color}`}
          >
            <ConfIcon className="w-3.5 h-3.5" />
            <span>{confBadge.label}</span>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white bg-slate-950 transition-colors"
            title="Copy answer"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Hallucination / Verification Metric Bar */}
      {metrics && metrics.total_claims > 0 && (
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-300 font-medium">
              Factual Grounding: <strong className="text-white">{metrics.summary_statement}</strong>
            </span>
            <span className="font-mono text-cyan-400 font-semibold">{metrics.support_ratio}% supported</span>
          </div>

          {/* Dual visual progress bar */}
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden flex">
            <div
              style={{ width: `${metrics.support_ratio || 0}%` }}
              className="bg-emerald-500 h-full transition-all duration-500"
              title={`Supported: ${metrics.supported}`}
            />
            <div
              style={{ width: `${metrics.contradiction_ratio || 0}%` }}
              className="bg-rose-500 h-full transition-all duration-500"
              title={`Contradicted: ${metrics.contradicted}`}
            />
            <div
              style={{
                width: `${
                  100 - (metrics.support_ratio || 0) - (metrics.contradiction_ratio || 0)
                }%`,
              }}
              className="bg-amber-500/80 h-full transition-all duration-500"
              title={`Uncertain/Pending: ${metrics.uncertain + (metrics.not_verifiable || 0)}`}
            />
          </div>

          <p className="text-[11px] text-slate-500 italic">
            * {metrics.calculation_note}
          </p>
        </div>
      )}

      {/* Formatted Synthesized Text */}
      <div className="text-sm sm:text-base text-slate-200 leading-relaxed font-sans prose prose-invert max-w-none whitespace-pre-wrap">
        {answer}
      </div>
    </div>
  );
}
