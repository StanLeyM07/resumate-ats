import { useState, useRef, useCallback } from 'react';

/*
  LEARNING MODULE: Drag-and-Drop API
  The HTML5 Drag & Drop API uses four key events:
  - onDragOver: fires continuously while an item is dragged over the target. Must call
    e.preventDefault() to allow the drop.
  - onDragEnter: fires when a dragged item enters the target boundary.
  - onDragLeave: fires when a dragged item leaves the target boundary.
  - onDrop: fires when the item is released over the target.
*/

export default function FileUpload({ selectedFiles, onFilesSelected, onRemoveFile, onProcess, isProcessing, disabled }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      onFilesSelected(droppedFiles);
    }
  }, [onFilesSelected]);

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    onFilesSelected(files);
    // Reset input so the same file can be selected again
    e.target.value = '';
  };

  return (
    <div className={`transition-all ${disabled ? 'opacity-50 pointer-events-none' : ''}`} aria-disabled={disabled}>
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload resume files"
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click(); }}
        onDragOver={handleDragOver}
        onDragEnter={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg py-2 px-4 flex items-center justify-center gap-3 cursor-pointer transition-all ${
          isDragOver
            ? 'border-cyan-400 bg-cyan-900/20 scale-[1.02]'
            : 'border-slate-600 hover:border-cyan-400 bg-slate-900/50 hover:bg-slate-800'
        }`}
      >
        <input ref={fileInputRef} type="file" multiple className="hidden" accept=".pdf,.docx,.txt" onChange={handleFileInput} />
        <svg className="w-5 h-5 text-cyan-500" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <div className="text-left flex items-center gap-2">
          <p className="font-semibold text-slate-200 text-sm m-0">
            {isDragOver ? 'Drop files here!' : 'Click or Drag Resumes Here'}
          </p>
          <p className="text-[10px] text-slate-500 m-0">PDF, DOCX, TXT (Max 500 files)</p>
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-4 flex flex-col space-y-3">
          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3 max-h-40 overflow-y-auto">
            {selectedFiles.map((f, i) => (
              <div key={`${f.name}-${f.size}`} className="flex justify-between items-center text-sm text-slate-300 mb-1 bg-slate-800/50 p-2 rounded">
                <span className="truncate pr-2">📄 {f.name}</span>
                <button onClick={() => onRemoveFile(i)} aria-label={`Remove ${f.name}`} className="text-red-400 hover:text-red-300 font-bold flex-shrink-0">✕</button>
              </div>
            ))}
          </div>
          <button
            onClick={onProcess}
            disabled={isProcessing}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 rounded-md transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] disabled:opacity-50"
          >
            {isProcessing ? "Processing..." : "Execute AI Scoring"}
          </button>
        </div>
      )}
    </div>
  );
}
