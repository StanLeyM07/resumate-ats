import { useState } from 'react';

/*
  LEARNING MODULE: Controlled Forms in React
  React "controlled components" means the form data is managed by React state.
  Here we use the `name` attribute + `FormData` API to collect values on submit,
  which is a simpler pattern for forms that don't need real-time field validation.
*/

export default function JobForm({ onJobCreated, apiUrl }) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const formData = new FormData(e.target);
    const payload = {
      title: formData.get('title'),
      required_skills: formData.get('skills'),
      min_experience_years: parseInt(formData.get('experience'), 10) || 0,
      education: formData.get('education'),
      additional_context: formData.get('context')
    };

    try {
      const res = await fetch(`${apiUrl}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const job = await res.json();
      onJobCreated(job);
    } catch (error) {
      console.error('Failed to create job:', error);
      throw error; // Let the parent handle the toast
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputClass = "w-full bg-slate-900/50 border border-slate-700 rounded-md p-2 text-white focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none transition-all";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="job-title" className="block text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Role Title</label>
        <input id="job-title" name="title" required className={inputClass} placeholder="Senior Backend Engineer" />
      </div>
      <div>
        <label htmlFor="job-skills" className="block text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Required Skills</label>
        <input id="job-skills" name="skills" required className={inputClass} placeholder="Python, FastAPI, Postgres" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="job-experience" className="block text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Min. Exp (Yrs)</label>
          <input id="job-experience" name="experience" type="number" required defaultValue="0" className={inputClass} />
        </div>
        <div>
          <label htmlFor="job-education" className="block text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Education</label>
          <input id="job-education" name="education" required className={inputClass} placeholder="BS Comp Sci" />
        </div>
      </div>
      <div>
        <label htmlFor="job-context" className="block text-xs font-semibold text-cyan-400 mb-1 uppercase tracking-wider">Context (Optional)</label>
        <textarea id="job-context" name="context" rows="3" className={inputClass} placeholder="Looking for leadership potential..." />
      </div>
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 rounded-md transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] disabled:opacity-50"
      >
        {isSubmitting ? 'Creating...' : 'Initialize AI Profile'}
      </button>
    </form>
  );
}
