import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { modelNameForDisease } from '../utils/modelNames'

export default function HealthForm() {
  const { token } = useAuth()
  const [formState, setFormState] = useState({
    age: '',
    glucose: '',
    blood_pressure: '',
    insulin: '',
    height: '',
    weight: '',
    bmi: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    async function loadProfileAge() {
      try {
        const profile = await apiRequest('/profile', token)
        if (profile.age !== null && profile.age !== undefined) {
          setFormState((previous) => ({ ...previous, age: String(profile.age) }))
        }
      } catch {
        // The assessment remains usable when no profile has been completed.
      }
    }
    loadProfileAge()
  }, [token])

  const calculateBmi = (height, weight) => {
    const h = Number(height)
    const w = Number(weight)
    if (h > 0 && w > 0) {
      return ((w / ((h / 100) ** 2)) || 0).toFixed(1)
    }
    return ''
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    const nextState = { ...formState, [name]: value }
    if (name === 'height' || name === 'weight') {
      nextState.bmi = calculateBmi(nextState.height, nextState.weight)
    }
    setFormState(nextState)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = {
        age: Number(formState.age),
        glucose: Number(formState.glucose),
        blood_pressure: Number(formState.blood_pressure),
        insulin: Number(formState.insulin),
        bmi: Number(formState.bmi),
      }
      const result = await apiRequest('/predict', token, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      navigate('/result', { state: { result } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h1 className="mb-2 text-2xl font-semibold text-[var(--text-primary)]">Diabetes Risk Assessment</h1>
        <p className="text-sm text-[var(--text-secondary)]">ML-based assessment using the trained {modelNameForDisease('diabetes')} model.</p>
        <p className="mt-2 text-xs text-[var(--text-muted)]">This application is an educational/research prototype for machine-learning-based risk prediction. It is not a medical diagnostic or treatment tool. Results should not be used for clinical decision-making.</p>
      </section>
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <form className="grid gap-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Age (years, from profile when available) *</span>
              <input 
                name="age" 
                type="number" 
                min="1"
                max="150"
                value={formState.age} 
                onChange={handleChange} 
                required 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition focus:border-[var(--brand)]" 
                placeholder="Enter your age"
              />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Glucose (mg/dL) *</span>
              <input 
                name="glucose" 
                type="number" 
                min="0"
                value={formState.glucose} 
                onChange={handleChange} 
                required 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition focus:border-[var(--brand)]" 
                placeholder="Fasting glucose level"
              />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Blood Pressure (mmHg) *</span>
              <input 
                name="blood_pressure" 
                type="number" 
                min="0"
                value={formState.blood_pressure} 
                onChange={handleChange} 
                required 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition focus:border-[var(--brand)]" 
                placeholder="Systolic BP"
              />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Insulin (mU/ml) *</span>
              <input 
                name="insulin" 
                type="number" 
                min="0"
                value={formState.insulin} 
                onChange={handleChange} 
                required 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition focus:border-[var(--brand)]" 
                placeholder="Fasting insulin"
              />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Height (cm) *</span>
              <input 
                name="height" 
                type="number" 
                min="0"
                value={formState.height} 
                onChange={handleChange} 
                required 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition focus:border-[var(--brand)]" 
                placeholder="Height"
              />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Weight (kg) *</span>
              <input 
                name="weight" 
                type="number" 
                min="0"
                value={formState.weight} 
                onChange={handleChange} 
                required 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition focus:border-[var(--brand)]" 
                placeholder="Weight"
              />
            </label>
            <label className="md:col-span-2">
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">BMI (Auto-calculated)</span>
              <input 
                name="bmi" 
                type="text" 
                value={formState.bmi} 
                readOnly 
                className="mt-0 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-elevated)] px-3 py-2 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none" 
                placeholder="BMI will be calculated from height and weight"
              />
            </label>
          </div>
          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">{error}</div>}
          <button 
            type="submit" 
            disabled={loading}
            className="rounded-xl bg-[var(--brand)] px-6 py-3 text-base font-semibold text-white shadow-sm transition hover:opacity-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Running Assessment...' : 'Run Diabetes Risk Assessment'}
          </button>
        </form>
      </section>
    </div>
  )
}
