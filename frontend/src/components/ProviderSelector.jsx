import React from 'react';
import { CheckSquare, Square, Cpu, Sparkles, KeyRound } from 'lucide-react';

export default function ProviderSelector({
  selectedProviders,
  setSelectedProviders,
  userKeys,
  onOpenKeysModal
}) {
  const providers = [
    {
      id: 'gemini',
      mockId: 'mock_gemini',
      name: 'Google Gemini',
      model: 'gemini-3.8-flash',
      hasKey: Boolean(userKeys?.gemini),
      color: 'from-blue-500/20 to-cyan-500/20 text-cyan-400 border-cyan-700/50',
    },
    {
      id: 'openai',
      mockId: 'mock_gpt',
      name: 'OpenAI GPT-4o',
      model: 'gpt-4o-mini',
      hasKey: Boolean(userKeys?.openai),
      color: 'from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-700/50',
    },
    {
      id: 'anthropic',
      mockId: 'mock_claude',
      name: 'Anthropic Claude',
      model: 'claude-3.5-sonnet',
      hasKey: Boolean(userKeys?.anthropic),
      color: 'from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-700/50',
    },
    {
      id: 'groq',
      mockId: 'groq',
      name: 'Groq LLaMA',
      model: 'llama-3.3-70b',
      hasKey: Boolean(userKeys?.groq),
      color: 'from-purple-500/20 to-indigo-500/20 text-purple-400 border-purple-700/50',
    },
  ];

  const isSelected = (id, mockId) => {
    return selectedProviders.includes(id) || selectedProviders.includes(mockId);
  };

  const toggleProvider = (id, mockId, hasKey) => {
    const targetId = hasKey ? id : mockId;
    const isCurrentlySelected = isSelected(id, mockId);

    if (isCurrentlySelected) {
      // Don't allow deselecting all
      if (selectedProviders.length <= 1) return;
      setSelectedProviders(selectedProviders.filter((p) => p !== id && p !== mockId));
    } else {
      setSelectedProviders([...selectedProviders, targetId]);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>Active LLM Providers</span>
        </label>
        <button
          type="button"
          onClick={onOpenKeysModal}
          className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 underline underline-offset-2"
        >
          <KeyRound className="w-3 h-3" />
          <span>Manage Keys</span>
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {providers.map((p) => {
          const active = isSelected(p.id, p.mockId);
          return (
            <div
              key={p.id}
              onClick={() => toggleProvider(p.id, p.mockId, p.hasKey)}
              className={`cursor-pointer rounded-lg border p-3 transition-all select-none flex flex-col justify-between ${
                active
                  ? 'bg-slate-900/90 border-slate-600 shadow-md ring-1 ring-cyan-500/30'
                  : 'bg-slate-950/60 border-slate-800/80 opacity-60 hover:opacity-90'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-semibold text-slate-200">{p.name}</span>
                {active ? (
                  <CheckSquare className="w-4 h-4 text-cyan-400 shrink-0" />
                ) : (
                  <Square className="w-4 h-4 text-slate-600 shrink-0" />
                )}
              </div>

              <div className="flex items-center justify-between text-xs mt-1">
                <span className="text-slate-400 font-mono text-[11px] truncate">{p.model}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                    p.hasKey
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {p.hasKey ? 'BYOK Live' : 'Demo Sim'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
