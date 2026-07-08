import { useState, useEffect } from 'react';

const PROVIDERS = {
  local: {
    name: 'Local Ollama',
    baseUrl: 'http://localhost:11434/v1',
    models: ['llama3.2', 'mistral', 'gemma2', 'qwen2.5', 'custom...']
  },
  nvidia: {
    name: 'NVIDIA NIM',
    baseUrl: 'https://integrate.api.nvidia.com/v1',
    models: ['meta/llama-3.1-8b-instruct', 'meta/llama-3.1-70b-instruct', 'mistralai/mixtral-8x22b-instruct-v0.1']
  },
  openai: {
    name: 'OpenAI',
    baseUrl: 'https://api.openai.com/v1',
    models: ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo']
  },
  gemini: {
    name: 'Google Gemini',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    models: ['gemini-1.5-flash', 'gemini-1.5-pro', 'custom...']
  },
  custom: {
    name: 'Custom Provider',
    baseUrl: '',
    models: ['custom...']
  }
};

export default function AISettingsModal({ isOpen, onClose, onSave }) {
  const [providerId, setProviderId] = useState('nvidia');
  const [modelName, setModelName] = useState(PROVIDERS['nvidia'].models[0]);
  const [customModel, setCustomModel] = useState('');
  const [customBaseUrl, setCustomBaseUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [hasApiKey, setHasApiKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      const savedSettings = localStorage.getItem('ai_settings');
      if (savedSettings) {
        try {
          const data = JSON.parse(savedSettings);
          // Find provider id by matching base URL
          const matchedProvider = Object.entries(PROVIDERS).find(([_, p]) => p.baseUrl === data.base_url);
          const pId = matchedProvider ? matchedProvider[0] : 'nvidia';
          setProviderId(pId);
          
          if (PROVIDERS[pId].models.includes(data.model_name)) {
            setModelName(data.model_name);
            setCustomModel('');
          } else {
            setModelName('custom...');
            setCustomModel(data.model_name);
          }
          
          if (pId === 'custom') {
            setCustomBaseUrl(data.base_url);
          }

          setApiKey(data.api_key || '');
          setHasApiKey(!!data.api_key);
        } catch (e) {
          console.error("Failed to parse settings", e);
        }
      }
    }
  }, [isOpen]);

  const handleProviderChange = (e) => {
    const newProvider = e.target.value;
    setProviderId(newProvider);
    setModelName(PROVIDERS[newProvider].models[0]);
    setCustomModel('');
    if (newProvider === 'custom') {
      setCustomBaseUrl('https://api.groq.com/openai/v1'); // Default example
    }
  };

  const handleSave = (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const finalModel = modelName === 'custom...' ? customModel : modelName;

    const payload = {
      provider_type: providerId === 'local' ? 'local' : 'cloud',
      provider_name: providerId === 'custom' ? 'Custom OpenAI-Compatible' : PROVIDERS[providerId].name,
      base_url: providerId === 'custom' ? customBaseUrl : PROVIDERS[providerId].baseUrl,
      model_name: finalModel,
      api_key: apiKey || '',
    };

    try {
      localStorage.setItem('ai_settings', JSON.stringify(payload));
      setHasApiKey(!!apiKey);
      onSave(); // Trigger callback to close modal
    } catch (err) {
      setError("Failed to save settings to browser.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const currentProvider = PROVIDERS[providerId];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="glass-panel p-6 max-w-md w-full glow-border rounded-xl shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-white mb-1">AI Configuration</h2>
        <p className="text-xs text-slate-400 mb-2">Configure your AI engine. These settings are saved strictly in your browser and are never shared.</p>
        
        <div className="bg-cyan-900/30 border border-cyan-800 rounded-md p-2 mb-4">
          <p className="text-[11px] text-cyan-200 m-0">
            <strong>💡 Tip:</strong> If you want a faster model or better accuracy, you can use your own API key below. If left blank, the system will use the default public fallback key for demonstrations!
          </p>
        </div>

        {error && <div className="bg-red-500/20 border border-red-500 text-red-400 p-2 rounded mb-3 text-xs">{error}</div>}

        <form onSubmit={handleSave} className="space-y-4">
          
          <div>
            <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">AI Provider</label>
            <select 
              value={providerId} 
              onChange={handleProviderChange}
              className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400"
            >
              <option value="nvidia">NVIDIA NIM (Free Models)</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Google Gemini</option>
              <option value="local">Local Ollama</option>
              <option value="custom">Custom API Endpoint</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Model</label>
            <select 
              value={modelName} 
              onChange={e => setModelName(e.target.value)}
              className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400 mb-2"
            >
              {currentProvider.models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
            
            {modelName === 'custom...' && (
              <input 
                value={customModel} 
                onChange={e => setCustomModel(e.target.value)} 
                placeholder="Enter custom model name..."
                required 
                className="w-full bg-slate-900/50 border border-slate-700 rounded-md p-1.5 text-sm text-white outline-none focus:border-cyan-400" 
              />
            )}
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">
              {providerId === 'custom' ? 'Base URL (Custom)' : 'Base URL (Auto-set)'}
            </label>
            <input 
              value={providerId === 'custom' ? customBaseUrl : currentProvider.baseUrl} 
              onChange={e => providerId === 'custom' && setCustomBaseUrl(e.target.value)}
              disabled={providerId !== 'custom'}
              className={`w-full rounded-md p-1.5 text-sm outline-none focus:border-cyan-400 ${
                providerId === 'custom' 
                  ? 'bg-slate-900/50 border border-slate-700 text-white' 
                  : 'bg-slate-800/50 border border-slate-700 text-slate-400 cursor-not-allowed'
              }`} 
            />
          </div>

          {providerId !== 'local' && (
            <div>
              <label className="block text-[10px] font-semibold text-cyan-400 mb-1 uppercase tracking-wider">
                {providerId === 'custom' ? 'API Key (Required)' : 'API Key (Optional)'}
              </label>
              <input 
                type="password"
                value={apiKey} 
                onChange={e => setApiKey(e.target.value)} 
                placeholder={hasApiKey ? "•••••••••••••••• (Leave blank to keep existing)" : "Enter your API Key here"}
                required={providerId === 'custom' && !hasApiKey}
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
