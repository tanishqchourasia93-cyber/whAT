import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Filter,
  ShieldAlert,
  Layers
} from 'lucide-react';

export default function ClaimExplorer({ claims }) {
  const [filter, setFilter] = useState('ALL');
  const [expandedClaimId, setExpandedClaimId] = useState(null);

  if (!claims || claims.length === 0) return null;

  const filteredClaims = claims.filter((c) => {
    if (filter === 'ALL') return true;
    return c.verification_status === filter;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'SUPPORTED':
        return {
          label: 'Supported',
          color: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80',
          icon: CheckCircle2,
        };
      case 'CONTRADICTED':
        return {
          label: 'Contradicted',
          color: 'bg-rose-950/80 text-rose-300 border-rose-800/80 animate-pulse',
          icon: XCircle,
        };
      case 'UNCERTAIN':
        return {
          label: 'Uncertain',
          color: 'bg-amber-950/80 text-amber-300 border-amber-800/80',
          icon: AlertCircle,
        };
      default:
        return {
          label: 'Not Verifiable',
          color: 'bg-slate-900 text-slate-400 border-slate-700',
          icon: HelpCircle,
        };
    }
  };

  const counts = {
    ALL: claims.length,
    SUPPORTED: claims.filter((c) => c.verification_status === 'SUPPORTED').length,
    CONTRADICTED: claims.filter((c) => c.verification_status === 'CONTRADICTED').length,
    UNCERTAIN: claims.filter((c) => c.verification_status === 'UNCERTAIN').length,
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 shadow-lg overflow-hidden space-y-4 p-4 sm:p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center space-x-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Claim-Level Verification Explorer</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Atomic propositions cross-checked against authoritative external evidence
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center space-x-1.5 overflow-x-auto text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-500 mr-1 shrink-0" />
          {[
            { id: 'ALL', label: 'All', count: counts.ALL },
            { id: 'SUPPORTED', label: 'Supported', count: counts.SUPPORTED },
            { id: 'CONTRADICTED', label: 'Contradicted', count: counts.CONTRADICTED },
            { id: 'UNCERTAIN', label: 'Uncertain', count: counts.UNCERTAIN },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                filter === f.id
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <span>{f.label}</span>
              <span className="ml-1.5 opacity-60 font-mono text-[10px]">({f.count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-2.5">
        {filteredClaims.map((claim) => {
          const badge = getStatusBadge(claim.verification_status);
          const StatusIcon = badge.icon;
          const isExpanded = expandedClaimId === claim.id;

          return (
            <div
              key={claim.id}
              className={`rounded-lg border transition-all ${
                claim.verification_status === 'CONTRADICTED'
                  ? 'border-rose-900/60 bg-rose-950/10 hover:bg-rose-950/20'
                  : 'border-slate-800/90 bg-slate-950/50 hover:bg-slate-900/40'
              }`}
            >
              <div
                onClick={() => setExpandedClaimId(isExpanded ? null : claim.id)}
                className="p-3.5 cursor-pointer flex items-start justify-between gap-3 select-none"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${badge.color}`}
                    >
                      <StatusIcon className="w-3 h-3" />
                      <span>{badge.label}</span>
                    </span>

                    <span className="text-[11px] text-slate-500 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      Claim by: <span className="text-slate-300 font-semibold">{claim.source_model}</span>
                    </span>

                    {claim.confidence_level && (
                      <span className="text-[10px] text-slate-400 font-mono">
                        [{claim.confidence_level}]
                      </span>
                    )}

                    {claim.models_contradicting && claim.models_contradicting.length > 0 && (
                      <span className="inline-flex items-center space-x-1 text-[11px] text-rose-400 bg-rose-950/80 px-2 py-0.5 rounded border border-rose-800/80">
                        <ShieldAlert className="w-3 h-3" />
                        <span>Contested by: {claim.models_contradicting.join(', ')}</span>
                      </span>
                    )}
                  </div>

                  <p className="text-sm font-medium text-slate-200 leading-snug">
                    "{claim.normalized_claim}"
                  </p>
                </div>

                <div className="text-slate-500 hover:text-slate-300 p-1">
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </div>

              {/* Detailed Breakdown when expanded */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-1 border-t border-slate-800/80 space-y-3 text-xs bg-slate-900/40">
                  {/* System Explanation */}
                  {claim.explanation && (
                    <div className="p-2.5 rounded-md bg-slate-900 border border-slate-800">
                      <span className="font-semibold text-slate-300 block mb-1">Verification Rationale:</span>
                      <p className="text-slate-400 leading-relaxed">{claim.explanation}</p>
                    </div>
                  )}

                  {/* Contradicting Evidence Alert */}
                  {claim.contradicting_evidence && claim.contradicting_evidence.length > 0 && (
                    <div className="p-3 rounded-md bg-rose-950/40 border border-rose-800/80 text-rose-200 space-y-1.5">
                      <div className="flex items-center space-x-1.5 font-semibold text-rose-300">
                        <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
                        <span>Conflicting Authoritative Evidence:</span>
                      </div>
                      {claim.contradicting_evidence.map((ev, i) => (
                        <div key={i} className="pl-5 space-y-1">
                          <p className="italic text-rose-100/90">"{ev.passage}"</p>
                          <a
                            href={ev.url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center space-x-1 text-rose-400 hover:text-rose-300 underline"
                          >
                            <span>Source: {ev.title} ({ev.domain})</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Supporting Evidence */}
                  {claim.supporting_evidence && claim.supporting_evidence.length > 0 && (
                    <div className="space-y-2">
                      <span className="font-semibold text-slate-300">Consulted External Records:</span>
                      {claim.supporting_evidence.map((ev, i) => (
                        <div key={i} className="p-2.5 rounded bg-slate-950/80 border border-slate-800 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-slate-200">{ev.title}</span>
                            <span className="text-[10px] text-cyan-400 font-mono bg-cyan-950 px-1.5 py-0.5 rounded border border-cyan-800/60">
                              Auth Score: {ev.authority_score}
                            </span>
                          </div>
                          <p className="text-slate-400 line-clamp-3">"{ev.passage}"</p>
                          <a
                            href={ev.url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 underline text-[11px]"
                          >
                            <span>{ev.domain}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
