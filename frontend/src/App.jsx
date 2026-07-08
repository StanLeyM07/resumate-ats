import { useState, useEffect, useRef, useCallback } from 'react';


import Navbar from './components/Navbar';
import JobForm from './components/JobForm';
import ActiveJobCard from './components/ActiveJobCard';
import FileUpload from './components/FileUpload';
import TerminalOutput from './components/TerminalOutput';
import CandidateCard from './components/CandidateCard';
import Toast from './components/Toast';
import AISettingsModal from './components/AISettingsModal';

// In production (when served by FastAPI), we use relative paths for API and dynamic host for WebSockets.
// In development, we fallback to localhost:8000
const isProd = import.meta.env.PROD;
const API_URL = import.meta.env.VITE_API_URL || (isProd ? '' : 'http://localhost:8000');

function App() {
  const [activeJob, setActiveJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [toast, setToast] = useState({ show: false, message: '', isError: false });
  
  // Settings State
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isConfigured, setIsConfigured] = useState(true);

  // Client ID for isolated WebSockets
  const clientIdRef = useRef(crypto.randomUUID ? crypto.randomUUID() : Date.now().toString());

  const wsRef = useRef(null);
  const toastTimerRef = useRef(null);

  // ---------------------------------------------------------------------------
  // Init from Local Storage
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const savedJob = localStorage.getItem('activeJob');
    const savedCandidates = localStorage.getItem('candidates');
    if (savedJob) setActiveJob(JSON.parse(savedJob));
    if (savedCandidates) setCandidates(JSON.parse(savedCandidates));
  }, []);

  // ---------------------------------------------------------------------------
  // Toast Helper
  // ---------------------------------------------------------------------------
  const showToast = useCallback((message, isError = false) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToast({ show: true, message, isError });
    toastTimerRef.current = setTimeout(() => {
      setToast({ show: false, message: '', isError: false });
    }, 3000);
  }, []);

  // ---------------------------------------------------------------------------
  // WebSocket Setup with Cleanup
  // ---------------------------------------------------------------------------
  const setupWebSocket = useCallback(() => {
    if (wsRef.current) wsRef.current.close();

    const host = isProd ? window.location.host : 'localhost:8000';
    const protocol = isProd && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const WS_URL = `${protocol}//${host}/ws/progress/${clientIdRef.current}`;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setTerminalLogs(prev => [...prev, { msg: data.message, status: data.status }]);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = () => console.error('WebSocket connection error');
    ws.onclose = () => console.log('WebSocket connection closed');
  }, []);

  // ---------------------------------------------------------------------------
  // Event Handlers
  // ---------------------------------------------------------------------------
  const handleJobCreated = useCallback((job) => {
    setActiveJob(job);
    localStorage.setItem('activeJob', JSON.stringify(job));
    setCandidates([]);
    localStorage.removeItem('candidates');
    setupWebSocket();
    showToast("Job Profile Created!");
  }, [setupWebSocket, showToast]);

  const handleClearDB = useCallback(() => {
    if (!confirm("Are you sure you want to clear your local workspace?")) return;
    setActiveJob(null);
    setCandidates([]);
    setTerminalLogs([]);
    setSelectedFiles([]);
    localStorage.removeItem('activeJob');
    localStorage.removeItem('candidates');
    showToast("Workspace Cleared!");
  }, [showToast]);

  const handleFilesSelected = useCallback((files) => {
    setSelectedFiles(prev => [...prev, ...files]);
  }, []);

  const handleRemoveFile = useCallback((index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleProcess = useCallback(async () => {
    if (!activeJob || selectedFiles.length === 0) return;
    setIsProcessing(true);
    setTerminalLogs([]);
    setupWebSocket(); // Ensure WS is open before starting
    
    // We append the existing candidates so we can add to them if we process more
    const currentCandidates = [...candidates];
    setCandidates([]);

    const formData = new FormData();
    selectedFiles.forEach(f => formData.append('files', f));
    
    // Append Job details directly to the form
    formData.append('client_id', clientIdRef.current);
    formData.append('job_title', activeJob.title);
    formData.append('job_skills', activeJob.required_skills);
    formData.append('job_experience', activeJob.min_experience_years.toString());
    formData.append('job_education', activeJob.education || '');
    formData.append('job_context', activeJob.additional_context || '');

    try {
      const headers = {};
      const savedSettings = localStorage.getItem('ai_settings');
      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings);
          if (settings.provider_type) headers['X-AI-Provider-Type'] = settings.provider_type;
          if (settings.provider_name) headers['X-AI-Provider-Name'] = settings.provider_name;
          if (settings.base_url) headers['X-AI-Base-Url'] = settings.base_url;
          if (settings.model_name) headers['X-AI-Model-Name'] = settings.model_name;
          if (settings.api_key) headers['X-AI-API-Key'] = settings.api_key;
        } catch (e) {
          console.error("Failed to parse settings", e);
        }
      }

      const res = await fetch(`${API_URL}/api/score_candidates`, {
        method: 'POST',
        headers: headers,
        body: formData
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `Server error: ${res.status}`);
      }

      const newCandidates = await res.json();
      
      // Merge with old candidates and resort
      const allCandidates = [...currentCandidates, ...newCandidates].sort((a, b) => b.score_data.match_score - a.score_data.match_score);
      setCandidates(allCandidates);
      localStorage.setItem('candidates', JSON.stringify(allCandidates));

    } catch (error) {
      setTerminalLogs(prev => [...prev, { msg: `Error: ${error.message}`, status: "error" }]);
      setCandidates(currentCandidates); // Restore old candidates on failure
    } finally {
      setSelectedFiles([]);
      setIsProcessing(false);
    }
  }, [activeJob, selectedFiles, candidates, setupWebSocket]);

  const handleExportCSV = useCallback(() => {
    if (candidates.length === 0) return;
    
    const headers = ["Candidate Name", "Match Score", "Verdict", "Years Exp", "Skills", "Key Strengths", "Concerns", "Filename"];
    const rows = candidates.map(c => [
      `"${c.score_data.candidate_name.replace(/"/g, '""')}"`,
      c.score_data.match_score,
      `"${c.score_data.verdict.replace(/"/g, '""')}"`,
      c.score_data.years_experience,
      `"${c.score_data.extracted_skills.join(", ").replace(/"/g, '""')}"`,
      `"${c.score_data.key_strengths.join(" | ").replace(/"/g, '""')}"`,
      `"${c.score_data.concerns.join(" | ").replace(/"/g, '""')}"`,
      `"${c.filename.replace(/"/g, '""')}"`
    ]);

    const csvContent = [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    
    link.setAttribute("href", url);
    link.setAttribute("download", `job_candidates_export.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [candidates]);

  const handleSettingsSaved = () => {
    setIsSettingsOpen(false);
    setIsConfigured(true);
    showToast("AI Configuration Saved!");
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="h-screen flex flex-col text-slate-100 p-4 lg:p-8 overflow-hidden">
      <AISettingsModal 
        isOpen={isSettingsOpen} 
        onClose={isConfigured ? () => setIsSettingsOpen(false) : null} 
        onSave={handleSettingsSaved}
        apiUrl={API_URL}
      />

      <div className={`flex flex-col h-full transition-all duration-500 ${!isConfigured ? 'blur-md opacity-50 pointer-events-none' : ''}`}>
        <div className="flex-none">
          <Navbar onClearDB={handleClearDB} onOpenSettings={() => setIsSettingsOpen(true)} />
        </div>

        <main className="flex-1 min-h-0 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-4 h-full flex flex-col space-y-4 overflow-y-auto pr-2 pb-4">
            <div className="glass-panel p-6 glow-border transition-all flex flex-col h-fit flex-none">
              <h2 className="text-xl font-bold text-white mb-1">1. Define the Role</h2>
              <p className="text-sm text-slate-400 mb-3">Create the target profile for AI scoring.</p>

              {!activeJob ? (
                <JobForm onJobCreated={handleJobCreated} />
              ) : (
                <ActiveJobCard job={activeJob} />
              )}
            </div>

            <div className="flex-none">
              <FileUpload
                selectedFiles={selectedFiles}
                onFilesSelected={handleFilesSelected}
                onRemoveFile={handleRemoveFile}
                onProcess={handleProcess}
                isProcessing={isProcessing}
                disabled={!activeJob}
              />
            </div>

            <div className="flex-1 flex flex-col min-h-[250px]">
              <TerminalOutput logs={terminalLogs} />
            </div>
          </div>

          <div className="lg:col-span-8 h-full flex flex-col space-y-4 min-h-0">
            {candidates.length > 0 ? (
              <div className="flex-1 glass-panel p-6 glow-border transition-all flex flex-col min-h-0">
                <div className="flex justify-between items-center mb-4 border-b border-slate-700 pb-3 flex-none">
                  <h3 className="text-xl font-bold text-white">Ranked Candidates</h3>
                  <button
                    onClick={handleExportCSV}
                    aria-label="Export candidates to CSV"
                    className="flex items-center gap-2 bg-slate-800 border border-slate-600 hover:border-cyan-400 text-cyan-400 px-3 py-1.5 rounded-md text-sm transition-all shadow-[0_0_10px_rgba(6,182,212,0.1)] hover:shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                  >
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="7 10 12 15 17 10"></polyline>
                      <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Export CSV
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto pr-2 space-y-4 min-h-0">
                  {candidates.map((c) => (
                    <CandidateCard key={c.id} candidate={c} />
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex-1 glass-panel p-6 glow-border flex items-center justify-center text-slate-500">
                <p>No candidates processed yet. Upload resumes and run AI scoring.</p>
              </div>
            )}
          </div>
        </main>
      </div>

      <Toast toast={toast} />
    </div>
  );
}

export default App;
