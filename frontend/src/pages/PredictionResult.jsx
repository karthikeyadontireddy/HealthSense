import { useLocation, Link } from 'react-router-dom'
import { modelNameForDisease } from '../utils/modelNames'

export default function PredictionResult() {
  const { state } = useLocation()
  const result = state?.result

  if (!result) {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Prediction Result</h1>
        <p className="mt-4 text-[var(--text-secondary)]">No prediction result found. Please complete the health assessment form first.</p>
        <Link to="/health" className="mt-6 inline-block rounded-xl bg-[var(--brand)] px-6 py-3 text-white font-medium">
          Go to Health Assessment
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Diabetes Risk Prediction</h1>
        <p className="text-sm text-[var(--text-secondary)]">ML-based assessment result from trained {modelNameForDisease('diabetes')} model</p>
        <p className="mt-2 text-xs text-[var(--text-muted)]">
          This application is an educational/research prototype. Results represent a model-estimated probability and should not be used for clinical decision-making.
        </p>
      </section>

      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <div className="space-y-6">
          <div className="border-b border-[var(--border-color)] pb-4">
            <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">Assessment Target</p>
            <p className="mt-1 text-3xl font-bold text-[var(--text-primary)]">Diabetes</p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">Model Probability</p>
              <p className="mt-2 text-4xl font-bold text-[var(--brand)]">{result.risk_percentage}%</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">Predicted risk category</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">Risk Category</p>
              <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{result.risk_level}</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">Based on model classification</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">Model Information</p>
              <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{modelNameForDisease(result.disease || 'diabetes', result.model_name)}</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">v{result.model_version}</p>
            </div>
          </div>

          <div className="border-t border-[var(--border-color)] pt-4">
            <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">Assessment Timestamp</p>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">{new Date(result.created_at).toLocaleString()}</p>
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-subtle)] p-6 shadow-[var(--shadow-soft)]">
        <p className="mb-4 font-semibold text-[var(--text-primary)]">Educational Information</p>
        <ul className="list-disc space-y-2 pl-5 text-[var(--text-secondary)]">
          {result.recommendations.map((item, index) => (
            <li key={index} className="text-sm">{item}</li>
          ))}
        </ul>
      </section>

      <section className="rounded-3xl border border-[var(--border-color)] bg-yellow-50 p-6 shadow-[var(--shadow-soft)] dark:bg-yellow-950/20 dark:border-yellow-900">
        <p className="font-semibold text-yellow-900 dark:text-yellow-200">⚠️ Important Disclaimer</p>
        <p className="mt-2 text-sm text-yellow-800 dark:text-yellow-300">
          This is a machine-learning model prediction for educational and research purposes only. 
          It is <strong>not a medical diagnosis</strong> and should <strong>not be used for clinical decision-making</strong>.
          Please consult with a qualified healthcare professional for medical advice.
        </p>
      </section>

      <div className="flex flex-col gap-3 sm:flex-row">
        <Link to="/history" className="flex-1 rounded-xl bg-[var(--brand)] px-6 py-3 text-center font-medium text-white transition hover:opacity-95">
          View Assessment History
        </Link>
        <Link to="/health" className="flex-1 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] px-6 py-3 text-center font-medium text-[var(--text-primary)] transition hover:bg-[var(--bg-subtle)]">
          New Assessment
        </Link>
      </div>
    </div>
  )
}
