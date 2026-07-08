export default function ActiveJobCard({ job }) {
  const skills = job?.required_skills?.split(',') || [];

  return (
    <div className="bg-slate-900/50 border border-slate-700 rounded-md p-4">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
        <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Active Profile</span>
      </div>
      <h3 className="text-lg font-bold text-white mb-2">{job.title}</h3>
      <div className="flex flex-wrap gap-2">
        {skills.map((s, i) => (
          <span key={s.trim()} className="bg-slate-800 border border-slate-600 text-xs px-2 py-1 rounded-full text-slate-300">
            {s.trim()}
          </span>
        ))}
      </div>
    </div>
  );
}
