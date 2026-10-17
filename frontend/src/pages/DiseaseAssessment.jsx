import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiRequest } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { modelNameForDisease } from '../utils/modelNames'

const labels = {
  age: 'Age', bp: 'Blood pressure', sg: 'Specific gravity', al: 'Albumin', su: 'Sugar',
  rbc: 'Red blood cells', pc: 'Pus cells', pcc: 'Pus cell clumps', ba: 'Bacteria',
  bgr: 'Random blood glucose', bu: 'Blood urea', sc: 'Serum creatinine', sod: 'Sodium',
  pot: 'Potassium', hemo: 'Hemoglobin', pcv: 'Packed cell volume', wbcc: 'White blood cell count',
  rbcc: 'Red blood cell count', htn: 'Hypertension', dm: 'Diabetes mellitus', cad: 'Coronary artery disease',
  appet: 'Appetite', pe: 'Pedal edema', ane: 'Anemia', Glucose: 'Glucose', BloodPressure: 'Blood pressure',
  Insulin: 'Insulin', BMI: 'Body mass index', Age: 'Age', sex: 'Sex', cp: 'Chest pain type',
  trestbps: 'Resting blood pressure', chol: 'Cholesterol', fbs: 'Fasting blood sugar', restecg: 'Resting ECG',
  thalach: 'Maximum heart rate', exang: 'Exercise-induced angina', oldpeak: 'ST depression', slope: 'ST slope', ca: 'Major vessels', thal: 'Thalassemia code',
}

const categoricalOptions = {
  sex: ['0', '1'], cp: ['1', '2', '3', '4'], fbs: ['0', '1'], restecg: ['0', '1', '2'], exang: ['0', '1'], slope: ['1', '2', '3'], ca: ['0', '1', '2', '3'], thal: ['3', '6', '7'],
  sg: ['1.005', '1.010', '1.015', '1.020', '1.025'], al: ['0', '1', '2', '3', '4', '5'], su: ['0', '1', '2', '3', '4', '5'],
  rbc: ['normal', 'abnormal'], pc: ['normal', 'abnormal'], pcc: ['present', 'notpresent'], ba: ['present', 'notpresent'],
  htn: ['yes', 'no'], dm: ['yes', 'no'], cad: ['yes', 'no'], appet: ['good', 'poor'], pe: ['yes', 'no'], ane: ['yes', 'no'],
}

const numericCategorical = new Set(['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal'])

function titleFor(id) {
  return id === 'heart_disease' ? 'Heart Disease Risk' : id === 'ckd' ? 'Chronic Kidney Disease Risk' : 'Diabetes Risk'
}

export default function DiseaseAssessment() {
  const { disease = 'diabetes' } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [model, setModel] = useState(null)
  const [values, setValues] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const models = await apiRequest('/models', token)
        const selected = models.find((item) => item.disease_id === disease)
        if (!selected) throw new Error('Disease model not found.')
        setModel(selected)
        setValues(Object.fromEntries(selected.feature_names.map((name) => [name, ''])))
      } catch (err) { setError(err.message) }
    }
    load()
  }, [disease, token])

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const features = Object.fromEntries(Object.entries(values).map(([name, value]) => [name, model.numeric_features.includes(name) || (disease === 'heart_disease' && numericCategorical.has(name)) ? Number(value) : value]))
      const invalidNumeric = model.numeric_features.find((name) => !Number.isFinite(features[name]) || features[name] < 0)
      if (invalidNumeric) throw new Error(`${labels[invalidNumeric] || invalidNumeric} must be a non-negative finite number.`)
      const result = await apiRequest(`/predict/${disease}`, token, { method: 'POST', body: JSON.stringify({ features }) })
      navigate('/result', { state: { result } })
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  if (error && !model) return <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700">{error}</div>
  if (!model) return <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6">Loading model contract...</div>

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--brand)]">Disease-specific assessment</p>
        <h1 className="mt-2 text-3xl font-semibold text-[var(--text-primary)]">{titleFor(disease)}</h1>
        <p className="mt-2 max-w-3xl text-sm text-[var(--text-secondary)]">Enter only the features used by the saved {modelNameForDisease(model.disease_id, model.model_name)} artifact. This produces a model-estimated output for research and educational use, not a medical diagnosis.</p>
      </section>
      <form onSubmit={submit} className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {model.feature_names.map((name) => {
            const categorical = model.categorical_features.includes(name)
            return <label key={name} className="block">
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">{labels[name] || name}</span>
              {categorical && categoricalOptions[name] ? <select required value={values[name] || ''} onChange={(event) => setValues((previous) => ({ ...previous, [name]: event.target.value }))} className="w-full">
                <option value="">Select value</option>{categoricalOptions[name].map((option) => <option key={option} value={option}>{option}</option>)}
              </select> : <input required type="number" step="any" value={values[name] || ''} onChange={(event) => setValues((previous) => ({ ...previous, [name]: event.target.value }))} className="w-full" />}
            </label>
          })}
        </div>
        {error && <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <button disabled={loading} className="mt-6 rounded-xl bg-[var(--brand)] px-6 py-3 font-semibold text-white disabled:opacity-50">{loading ? 'Running model...' : 'Run model assessment'}</button>
      </form>
    </div>
  )
}
