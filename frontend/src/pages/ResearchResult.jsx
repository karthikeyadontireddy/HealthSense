import { Link, useLocation } from 'react-router-dom'
import { modelNameForDisease } from '../utils/modelNames'

export default function ResearchResult() {
  const { state } = useLocation()
  const result = state?.result
  if (!result) return <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6">No model output found. <Link className="text-[var(--brand)]" to="/dashboard">Return to dashboard</Link>.</div>
  const displayName = result.display_name || `${String(result.disease || 'Health').replaceAll('_', ' ')} Risk`
  const diseaseName = displayName.replace(/\s+risk$/i, '')
  const positiveProbability = result.positive_class_probability ?? result.probability
  const percentage = positiveProbability === null || positiveProbability === undefined ? null : positiveProbability * 100
  const importance = (result.feature_importance || []).slice(0, 8)
  const interpretation = percentage === null
    ? 'Estimated likelihood unavailable'
    : percentage < 30
      ? 'Lower estimated likelihood'
      : percentage < 70
        ? 'Intermediate estimated likelihood'
        : 'Higher estimated likelihood'

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-7 shadow-[var(--shadow-soft)]">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--brand)]">Research result</p>
        <h1 className="mt-2 text-3xl font-semibold">{diseaseName} Risk Estimate</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">This is a model-estimated likelihood based on the information entered. It is not a medical diagnosis or a clinically calibrated risk score.</p>
      </section>

      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-7 shadow-[var(--shadow-soft)]">
        <div className="grid items-center gap-8 md:grid-cols-[220px_1fr]">
          <div className="relative mx-auto flex h-52 w-52 items-center justify-center rounded-full" style={{ background: `conic-gradient(var(--brand) ${Math.max(0, Math.min(100, percentage || 0))}%, var(--bg-elevated) 0)` }}>
            <div className="flex h-40 w-40 flex-col items-center justify-center rounded-full bg-[var(--bg-surface)]"><span className="text-5xl font-semibold tracking-tight text-[var(--brand)]">{percentage === null ? 'n/a' : `${percentage.toFixed(1)}%`}</span><span className="mt-1 text-xs uppercase tracking-widest text-[var(--text-muted)]">estimated likelihood</span></div>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Simple interpretation</p>
            <h2 className="mt-2 text-2xl font-semibold">{interpretation}</h2>
            <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">This label is only a presentation category for the model output. The 30% and 70% boundaries are not medically validated risk thresholds.</p>
            {percentage !== null && <div className="mt-5"><div className="flex justify-between text-xs text-[var(--text-muted)]"><span>0%</span><span>30%</span><span>70%</span><span>100%</span></div><div className="mt-2 h-3 overflow-hidden rounded-full bg-[var(--bg-elevated)]"><div className="h-full rounded-full bg-[var(--brand)]" style={{ width: `${Math.max(0, Math.min(100, percentage))}%` }} /></div></div>}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-subtle)] p-6">
        <h2 className="text-xl font-semibold">What you can do</h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">General health information only. These suggestions are not personalized treatment advice.</p>
        <ul className="mt-4 grid gap-3 text-sm text-[var(--text-secondary)] sm:grid-cols-2"><li className="rounded-xl bg-[var(--bg-surface)] p-4">Maintain a balanced diet.</li><li className="rounded-xl bg-[var(--bg-surface)] p-4">Stay physically active according to your abilities.</li><li className="rounded-xl bg-[var(--bg-surface)] p-4">Maintain regular health check-ups.</li><li className="rounded-xl bg-[var(--bg-surface)] p-4">Discuss concerning symptoms or risk factors with a qualified healthcare professional.</li></ul>
      </section>

      <details className="group rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] shadow-[var(--shadow-soft)]">
        <summary className="cursor-pointer list-none p-6 font-semibold text-[var(--text-primary)]"><span className="flex items-center justify-between">Technical / Research Details<span className="text-xl text-[var(--text-muted)] transition group-open:rotate-45">+</span></span></summary>
        <div className="border-t border-[var(--border-color)] p-6">
          <div className="grid gap-4 sm:grid-cols-2"><div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Model</p><p className="mt-1 font-medium">{modelNameForDisease(result.disease, result.model_name || 'Not available')}</p></div><div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Artifact / version</p><p className="mt-1 font-medium">{result.model_version || 'Not available'}</p></div><div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Model class</p><p className="mt-1 font-medium">{String(result.prediction_class ?? result.risk_level ?? 'Not available')}</p></div><div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Positive-class probability</p><p className="mt-1 font-medium">{positiveProbability === null || positiveProbability === undefined ? 'Not available' : `${positiveProbability * 100}%`}</p></div></div>
          <div className="mt-6 border-t border-[var(--border-color)] pt-6"><h2 className="text-lg font-semibold">Model feature importance</h2><p className="mt-1 text-sm text-[var(--text-secondary)]">This describes model behavior and does not prove causation.</p><div className="mt-5 space-y-3">{importance.length === 0 ? <p className="text-sm text-[var(--text-muted)]">Feature importance is not available for this result.</p> : importance.map((item) => <div key={item.feature}><div className="flex justify-between gap-4 text-sm"><span className="break-all">{item.feature}</span><span>{item.importance.toFixed(3)}</span></div><div className="mt-1 h-2 rounded-full bg-[var(--bg-subtle)]"><div className="h-2 rounded-full bg-[var(--brand)]" style={{ width: `${Math.min(100, Math.max(0, item.importance * 100))}%` }} /></div></div>)}</div></div>
          <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900 dark:border-amber-900 dark:bg-amber-950/20 dark:text-amber-200">{result.research_disclaimer || 'Research/educational ML output only. This does not establish whether a person has a medical condition and is not a medical diagnosis.'} Model probabilities have not been clinically calibrated. Do not use this output to change medication, treatment, or urgent care decisions.</div>
        </div>
      </details>

      <p className="text-center text-xs leading-5 text-[var(--text-muted)]">Assessment recorded {result.created_at ? new Date(result.created_at).toLocaleString() : 'at the time of prediction'}.</p>
      <div className="flex flex-col gap-3 sm:flex-row"><Link to="/history" className="flex-1 rounded-xl bg-[var(--brand)] px-6 py-3 text-center font-medium text-white transition hover:opacity-95">View Assessment History</Link><Link to="/health" className="flex-1 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] px-6 py-3 text-center font-medium text-[var(--text-primary)] transition hover:bg-[var(--bg-subtle)]">New Assessment</Link></div>
    </div>
  )
}
