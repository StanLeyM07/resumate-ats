import { useState, useEffect } from 'react';

export default function AISettingsModal({ isOpen, onClose, onSave, apiUrl }) {
  const [providerType, setProviderType] = useState('local');
  const [providerName, setProviderName] = useState('Ollama');
  const [baseUrl, setBaseUrl] = useState('http://localhost:11434/v1');
  const [modelName, setModelName] = useState('llama3.2');
  const [apiKey, setApiKey] = useState('');
  const [hasApiKey, setHasApiKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      // Fetch current settings if they exist
      fetch(`${apiUrl}/settings`)
        .then(res => {
          if (res.ok) return res.json();
          throw new Error('Settings not configured');
        })
        .then(data => {
          setProviderType(data.provider_type);
          setProviderName(data.provider_name);
          setBaseUrl(data.base_url);
          setModelName(data.model_name);
          setHasApiKey(data.has_api_key);
        })
        .catch(() => {
          // Defaults are already set
        });
    }
  }, [isOpen, apiUrl]);

  const handleProviderTypeChange = (type) => {
    setProviderType(type);
    if (type === 'local') {
      setProviderName('Ollama');
      setBaseUrl('http://localhost:11434/v1');
      setModelName('llama3.2');
    } else {
      setProviderName('NVIDIA NIM');
      setBaseUrl('https://integrate.api.nvidia.com/v1');
      setModelName('meta/llama-3.1-70b-instruct');
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const payload = {
      provider_type: providerType,
      provider_name: providerName,
      base_url: baseUrl,
      model_name: modelName,
      api_key: apiKey || null,
    };

    try {
      const res = await fetch(`${apiUrl}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error('Failed to save settings');
      }

      onSave(); // Trigger callback to close modal / update app state
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="glass-panel p-6 max-w-md w-full glow-border rounded-xl shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-white mb-1">AI Configuration</h2>
        <p className="text-xs text-slate-400 mb-4">Select your preferred AI engine. API Keys are encrypted before being stored.</p>
        
        {error && <div className="bg-red-500/20 border border-red-500 text-red-400 p-2 rounded mb-3 text-xs">{error}</div>}

        <form onSubmit={handleSave} className="space-y-3">
          <div className="flex gap-2 p-1 bg-slate-900/50 rounded-lg">
            <button
              type="button"
              onClick={() => handleProviderTypeChange('local')}
              className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${
                providerType === 'local' ? 'bg-cyan-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
              }`}
            >
              Local Model
            </button>
            <button
              type="button"
              onClick={() => handleProviderTypeChange('cloud')}
              className={`flex-1 py-1.5 text-xs font-bold rounded-md transition-all ${
                providerType === 'cloud' ? 'bg-cyan-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
              }`}
            >
              Cloud Provider
            </button>
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Provider Name</label>
            <input 
              value={providerName} 
              onChange={e => setProviderName(e.target.value)} 
              required 
              className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400" 
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Base URL</label>
            <input 
              value={baseUrl} 
              onChange={e => setBaseUrl(e.target.value)} 
              required 
              className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400" 
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Model Name</label>
            <input 
              value={modelName} 
              onChange={e => setModelName(e.target.value)} 
              required 
              className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400" 
            />
          </div>

          {providerType === 'cloud' && (
            <div>
              <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">API Key</label>
              <input 
                type="password"
                value={apiKey} 
                onChange={e => setApiKey(e.target.value)} 
                placeholder={hasApiKey ? "•••••••••••••••• (Leave blank to keep existing)" : "Enter API Key"}
                required={!hasApiKey}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400" 
              />
            </div>
          )}

          <div className="pt-2 flex gap-3">
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="flex-1 border border-slate-600 text-slate-300 py-1.5 text-sm rounded-md hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={isLoading}
              className={`flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-1.5 text-sm rounded-md shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all ${isLoading ? 'opacity-50' : ''}`}
            >
              {isLoading ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
