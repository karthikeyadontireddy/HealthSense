import { useEffect, useState } from 'react'
import { apiRequest } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { modelNameForDisease } from '../utils/modelNames'

const diseaseNames = { diabetes: 'Diabetes', heart_disease: 'Heart Disease', ckd: 'Chronic Kidney Disease' }

export default function History() {
  const { token } = useAuth()
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadHistory() {
      setError('')
      try {
        const data = await apiRequest('/history', token)
        setHistory(data)
      } catch (err) {
        setError(err.message)
      }
    }
    loadHistory()
  }, [token])

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Prediction History</h1>
        <p className="text-sm text-[var(--text-secondary)]">Review saved outputs from the three disease-specific research model pipelines.</p>
      </section>
      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
      <section className="space-y-4">
        {history.length === 0 ? (
          <div className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 text-[var(--text-secondary)] shadow-[var(--shadow-soft)]">No prediction history yet.</div>
        ) : (
          history.map((item) => (
            <div key={item.id} className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-[var(--text-secondary)]">{new Date(item.created_at).toLocaleString()}</p>
                  <p className="mt-1 text-xl font-semibold text-[var(--text-primary)]">{diseaseNames[item.disease] || item.disease} assessment</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{item.risk_level}</p>
                </div>
                <p className="rounded-full bg-[var(--bg-subtle)] px-4 py-2 text-sm text-[var(--text-primary)]">{item.risk_percentage}%</p>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3 text-sm text-[var(--text-secondary)]">
                <div>Model: {modelNameForDisease(item.disease, item.model_name)} · {item.model_version}</div>
                {Object.entries(item.input_data || {}).map(([feature, value]) => <div key={feature}>{feature}: {String(value)}</div>)}
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  )
}
