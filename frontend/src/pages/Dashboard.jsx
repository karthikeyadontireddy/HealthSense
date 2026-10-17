import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { modelNameForDisease } from '../utils/modelNames'

const diseaseNames = { diabetes: 'Diabetes', heart_disease: 'Heart Disease', ckd: 'Chronic Kidney Disease' }

function Metric({ label, value }) {
  return <div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">{label}</p><p className="mt-1 text-lg font-semibold">{value === null || value === undefined ? 'n/a' : typeof value === 'number' ? value.toFixed(3) : value}</p></div>
}

export default function Dashboard() {
  const { token } = useAuth()
  const [models, setModels] = useState([])
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([apiRequest('/models', token), apiRequest('/history', token)]).then(([m, h]) => { setModels(m); setHistory(h) }).catch((err) => setError(err.message)) }, [token])

  return <div className="space-y-6">
    <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-7 shadow-[var(--shadow-soft)]">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--brand)]">HealthSense / research workspace</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Multi-disease ML research dashboard</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">Three independent supervised pipelines, each with its own dataset, preprocessing contract, saved artifact, and evaluation record.</p></div><div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-subtle)] px-4 py-3 text-sm text-[var(--text-secondary)]">Educational and research use only</div></div>
    </section>
    {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
    <section className="grid gap-4 lg:grid-cols-3">
      {models.map((model) => { const metrics = model.evaluation_metrics || {}; return <article key={model.disease_id} className="flex flex-col rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-[var(--shadow-soft)]"><div className="flex items-start justify-between gap-3"><div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Disease model</p><h2 className="mt-2 text-xl font-semibold">{diseaseNames[model.disease_id] || model.display_name}</h2></div><span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">{model.training_status === 'trained artifact available' ? 'Trained artifact' : model.training_status}</span></div><p className="mt-4 text-sm text-[var(--text-secondary)]">{modelNameForDisease(model.disease_id, model.model_name)} · {model.model_version}</p><div className="mt-5 grid grid-cols-2 gap-4"><Metric label="Test accuracy" value={metrics.accuracy} /><Metric label="ROC-AUC" value={metrics.roc_auc} /><Metric label="Train rows" value={model.training_sample_count} /><Metric label="Test rows" value={model.test_sample_count} /></div><div className="mt-5 flex gap-2"><Link to={`/assessment/${model.disease_id}`} className="flex-1 rounded-xl bg-[var(--brand)] px-4 py-2.5 text-center text-sm font-semibold text-white">Assess</Link><Link to="/history" className="rounded-xl border border-[var(--border-color)] px-4 py-2.5 text-sm">History</Link></div></article> })}
    </section>
    <section className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
      <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6"><div className="flex items-center justify-between"><div><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Recent model outputs</p><h2 className="mt-1 text-xl font-semibold">Assessment history</h2></div><Link to="/history" className="text-sm font-semibold text-[var(--brand)]">View all</Link></div>{history.length ? <div className="mt-5 space-y-3">{history.slice(0, 5).map((item) => <div key={item.id} className="flex items-center justify-between rounded-xl bg-[var(--bg-subtle)] px-4 py-3"><div><p className="font-medium">{diseaseNames[item.disease] || item.disease}</p><p className="text-xs text-[var(--text-muted)]">{modelNameForDisease(item.disease, item.model_name)} · {new Date(item.created_at).toLocaleString()}</p></div><span className="text-sm font-semibold">{item.risk_level}</span></div>)}</div> : <p className="mt-5 text-sm text-[var(--text-secondary)]">No saved model outputs yet.</p>}</div>
      <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6"><p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">Research guardrails</p><h2 className="mt-1 text-xl font-semibold">Interpret with care</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-[var(--text-secondary)]"><li>Outputs are model-estimated risk or class predictions.</li><li>They are not medical diagnoses or clinically validated assessments.</li><li>Feature importance describes model behavior, not causation.</li><li>Probability calibration has not been established.</li></ul></div>
    </section>
  </div>
}
