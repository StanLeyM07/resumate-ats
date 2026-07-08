import { useRef, useEffect } from 'react';

export default function TerminalOutput({ logs }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getColorClass = (status) => {
    if (status === 'processing') return 'text-yellow-400';
    if (status === 'success' || status === 'complete') return 'text-emerald-400';
    if (status === 'error') return 'text-red-400';
    return 'text-slate-400';
  };

  return (
    <div className="h-full flex flex-col bg-black border border-slate-800 rounded-lg overflow-hidden shadow-2xl">
      <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex justify-between items-center flex-none">
        <span className="text-xs font-mono text-slate-400">AI Terminal</span>
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
        </div>
      </div>
      <div className="flex-1 p-4 overflow-y-auto min-h-0 font-mono text-sm space-y-1" role="log" aria-live="polite">
        {logs.map((log, i) => (
          <div key={i} className={getColorClass(log.status)}>{`> ${log.msg}`}</div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
