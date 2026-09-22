import React, { useState } from 'react';
import { X, Key, Check, AlertCircle, Loader2, ShieldCheck, Trash2, ExternalLink } from 'lucide-react';
import { testProviderKey } from '../services/api';

export default function ApiKeyModal({ isOpen, onClose, userKeys, onSaveKeys, onClearKeys }) {
  const [keys, setKeys] = useState({
    gemini: userKeys?.gemini || '',
    openai: userKeys?.openai || '',
    anthropic: userKeys?.anthropic || '',
    groq: userKeys?.groq || '',
  });

  const [testStatus, setTestStatus] = useState({});
  const [testing, setTesting] = useState({});

  if (!isOpen) return null;

  const handleTest = async (providerId) => {
    const key = keys[providerId];
    if (!key || !key.trim()) {
      setTestStatus((prev) => ({ ...prev, [providerId]: { success: false, message: 'Please enter a key first' } }));
      return;
    }

    setTesting((prev) => ({ ...prev, [providerId]: true }));
    try {
      const res = await testProviderKey(providerId, key.trim());
      setTestStatus((prev) => ({
        ...prev,
        [providerId]: {
          success: res.status === 'success',
          message: res.message || (res.status === 'success' ? 'Connected successfully!' : 'Auth failed'),
        },
      }));
    } catch (err) {
      setTestStatus((prev) => ({
        ...prev,
        [providerId]: { success: false, message: err.message || 'Connection test failed' },
      }));
    } finally {
      setTesting((prev) => ({ ...prev, [providerId]: false }));
    }
  };

  const handleSave = () => {
    onSaveKeys(keys);
    onClose();
  };

  const maskDisplay = (val) => {
    if (!val || val.length <= 8) return '';
    return `${val.slice(0, 4)}••••••••${val.slice(-4)}`;
  };

  const providerConfigs = [
    {
      id: 'gemini',
      name: 'Google Gemini',
      placeholder: 'AIzaSy...',
      docsUrl: 'https://aistudio.google.com/app/apikey',
      note: 'Powers gemini-3.8-flash',
    },
    {
      id: 'openai',
      name: 'OpenAI',
      placeholder: 'sk-proj-...',
      docsUrl: 'https://platform.openai.com/api-keys',
      note: 'Powers gpt-4o & gpt-4o-mini',
    },
    {
      id: 'anthropic',
      name: 'Anthropic Claude',
      placeholder: 'sk-ant-...',
      docsUrl: 'https://console.anthropic.com/settings/keys',
      note: 'Powers claude-3-5-sonnet',
    },
    {
      id: 'groq',
      name: 'Groq LLaMA',
      placeholder: 'gsk_...',
      docsUrl: 'https://console.groq.com/keys',
      note: 'Powers llama-3.3-70b',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-5 relative">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800/80 flex items-center justify-center text-cyan-400">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Bring Your Own Key (BYOK)</h2>
              <p className="text-xs text-slate-400">Direct API connections with client-side isolation</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Security notice */}
        <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start space-x-2.5 text-xs text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold text-slate-300">Security & Billing Protocol:</span>
            <p>
              Keys are stored strictly in your local browser storage and dispatched only via secure headers to
              their respective endpoints. Raw keys are never stored on external databases or logged. Usage incurs standard API charges from your provider.
            </p>
          </div>
        </div>

        {/* Inputs */}
        <div className="space-y-3.5 max-h-96 overflow-y-auto pr-1">
          {providerConfigs.map((p) => (
            <div key={p.id} className="space-y-1.5 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-semibold text-slate-200">{p.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">({p.note})</span>
                </div>
                <a
                  href={p.docsUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-cyan-400 hover:underline flex items-center space-x-1"
                >
                  <span>Get Key</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="password"
                  value={keys[p.id] || ''}
                  onChange={(e) => setKeys({ ...keys, [p.id]: e.target.value })}
                  placeholder={maskDisplay(keys[p.id]) || p.placeholder}
                  className="flex-1 bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
                />

                <button
                  type="button"
                  onClick={() => handleTest(p.id)}
                  disabled={testing[p.id] || !keys[p.id]}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-1 transition-colors shrink-0"
                >
                  {testing[p.id] ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <span>Test</span>
                  )}
                </button>
              </div>

              {testStatus[p.id] && (
                <div
                  className={`text-[11px] flex items-center space-x-1 ${
                    testStatus[p.id].success ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {testStatus[p.id].success ? <Check className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                  <span>{testStatus[p.id].message}</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Modal Actions */}
        <div className="flex items-center justify-between border-t border-slate-800 pt-3">
          <button
            type="button"
            onClick={() => {
              setKeys({ gemini: '', openai: '', anthropic: '', groq: '' });
              onClearKeys();
            }}
            className="flex items-center space-x-1.5 text-xs text-rose-400 hover:text-rose-300 px-2 py-1"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Stored Keys</span>
          </button>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-md shadow-cyan-950/40"
            >
              Save Credentials
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
