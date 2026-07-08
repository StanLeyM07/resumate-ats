export default function Toast({ toast }) {
  if (!toast.show) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`fixed bottom-8 right-8 px-6 py-3 rounded-lg text-white font-semibold shadow-2xl transition-all border z-50 ${
        toast.isError ? 'bg-red-900 border-red-500' : 'bg-slate-800 border-slate-600'
      }`}
    >
      {toast.message}
    </div>
  );
}
