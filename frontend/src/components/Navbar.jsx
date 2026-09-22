import React from 'react';
import { ShieldCheck, Key, FileText, BarChart3, Search, Sparkles } from 'lucide-react';

export default function Navbar({ currentTab, setCurrentTab, onOpenApiKeyModal, hasKeys }) {
  const navItems = [
    { id: 'research', label: 'Research Studio', icon: Search },
    { id: 'documents', label: 'Doc Grounding', icon: FileText },
    { id: 'eval', label: 'Academic Benchmark', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('research')}>
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white font-mono">Veri<span className="text-cyan-400">AI</span></span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 font-mono">v1.0</span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Multi-LLM Research & Hallucination Verification Platform</p>
          </div>
        </div>

        <nav className="flex items-center space-x-1 sm:space-x-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}

          <div className="h-6 w-px bg-slate-800 mx-2" />

          <button
            onClick={onOpenApiKeyModal}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium border transition-all ${
              hasKeys
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/70 hover:bg-emerald-900/50'
                : 'bg-slate-900 text-slate-300 border-slate-700 hover:bg-slate-800 hover:text-white'
            }`}
          >
            <Key className="w-4 h-4" />
            <span className="hidden md:inline">BYOK Keys</span>
            {hasKeys && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />}
          </button>
        </nav>
      </div>
    </header>
  );
}
