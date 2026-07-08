export default function CandidateCard({ candidate }) {
  const { score_data, filename } = candidate;
  const score = score_data?.match_score ?? 0;

  let scoreColor = "text-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.4)] border-emerald-500/50";
  if (score < 80) scoreColor = "text-yellow-400 shadow-[0_0_15px_rgba(250,204,21,0.4)] border-yellow-500/50";
  if (score < 60) scoreColor = "text-red-400 shadow-[0_0_15px_rgba(248,113,113,0.4)] border-red-500/50";

  return (
    <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-5 flex gap-6 hover:border-cyan-500/50 transition-colors">
      <div className={`w-16 h-16 shrink-0 rounded-full flex items-center justify-center text-xl font-black bg-slate-950 border-2 ${scoreColor}`}>
        {score}
      </div>
      <div className="flex-1">
        <div className="mb-2">
          <h4 className="text-xl font-bold text-white mb-2">
            {score_data.candidate_name}
            <span className="text-xs font-normal text-slate-500 ml-2">{filename}</span>
          </h4>
          <span className="inline-block bg-slate-800 border border-slate-600 text-sm font-bold px-3 py-1 rounded text-cyan-300 mb-2 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
            {score_data.verdict}
          </span>
        </div>
        <p className="text-sm text-slate-400 mb-4">
          {score_data.years_experience} Yrs Exp • {(score_data.extracted_skills || []).join(', ')}
        </p>

        <div className="space-y-4 text-sm bg-black/50 p-4 rounded-lg border border-slate-700">
          <div>
            <span className="text-emerald-400 font-bold block mb-2 text-base">✓ Key Strengths</span>
            <ul className="list-disc pl-5 text-slate-200 space-y-1">
              {(score_data.key_strengths || []).map((s, idx) => <li key={idx}>{s}</li>)}
            </ul>
          </div>
          <div>
            <span className="text-red-400 font-bold block mb-2 text-base">⚠️ Concerns / Gaps</span>
            <ul className="list-disc pl-5 text-slate-200 space-y-1">
              {(score_data.concerns || []).map((s, idx) => <li key={idx}>{s}</li>)}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
