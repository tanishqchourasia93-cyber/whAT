import React from 'react';
import { Search, Loader2, Sparkles, CornerDownLeft } from 'lucide-react';

export default function QuestionInput({
  question,
  setQuestion,
  onSearch,
  loading,
  mode
}) {
  const sampleQueries = [
    {
      label: 'Taj Mahal Location & Architect',
      query: 'Where is the Taj Mahal located, who commissioned it, and who was the chief architect?',
    },
    {
      label: 'iPhone Launch Date (Disagreement Test)',
      query: 'What year was the original Apple iPhone officially released for public sale?',
    },
    {
      label: 'RISC-V vs ARM Licensing',
      query: 'What are the architectural licensing differences and advantages of RISC-V over ARM?',
    },
    {
      label: 'Nuclear vs Fossil Safety',
      query: 'Is nuclear energy empirically safer than fossil fuels per terawatt-hour produced?',
    },
  ];

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!loading && question.trim()) {
        onSearch();
      }
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative rounded-xl border border-slate-700/80 bg-slate-900/70 shadow-lg focus-within:border-cyan-500 focus-within:ring-1 focus-within:ring-cyan-500/50 transition-all">
        <textarea
          rows={3}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a factual question to verify across multiple LLMs and external evidence..."
          className="w-full bg-transparent px-4 pt-3.5 pb-12 text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none resize-none"
        />

        <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between">
          <div className="text-[11px] text-slate-500 flex items-center space-x-1 hidden sm:flex">
            <span>Press</span>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono text-[10px]">Enter</kbd>
            <span>to research, Shift+Enter for new line</span>
          </div>

          <button
            type="button"
            onClick={onSearch}
            disabled={loading || !question.trim()}
            className={`ml-auto flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-md ${
              loading || !question.trim()
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/60'
                : 'bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-cyan-950/50 cursor-pointer active:scale-95'
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Research & Verify</span>
                <CornerDownLeft className="w-3.5 h-3.5 opacity-70" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Preset benchmark queries */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-500 flex items-center space-x-1 shrink-0">
          <Sparkles className="w-3 h-3 text-cyan-400" />
          <span>Benchmark Demos:</span>
        </span>
        {sampleQueries.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => setQuestion(item.query)}
            className="shrink-0 px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 hover:border-slate-700 transition-colors"
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
