import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'
import { Link, useNavigate } from 'react-router-dom'

export default function Settings() {
  const { theme, setTheme } = useTheme()
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Settings</h1>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Configure the appearance and review the research prototype disclaimer.
        </p>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Appearance</h2>
          <div className="mt-4 space-y-3">
            {['light', 'dark', 'system'].map((option) => (
              <button
                key={option}
                onClick={() => setTheme(option)}
                className={`flex w-full items-center justify-between rounded-2xl border px-4 py-3 text-sm font-medium transition ${
                  theme === option
                    ? 'border-[var(--brand)] bg-[var(--brand-soft)] text-[var(--brand)]'
                    : 'border-[var(--border-color)] bg-transparent text-[var(--text-secondary)]'
                }`}
              >
                <span className="capitalize">{option}</span>
                <span>{theme === option ? '✓' : ''}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Account</h2>
          <div className="mt-4 space-y-3">
            <Link to="/profile" className="flex items-center justify-between rounded-2xl border border-[var(--border-color)] bg-[var(--bg-subtle)] px-4 py-3 text-sm text-[var(--text-primary)]">
              <span>Profile</span>
              <span>→</span>
            </Link>
            <button onClick={handleLogout} className="flex w-full items-center justify-between rounded-2xl border border-[var(--border-color)] bg-transparent px-4 py-3 text-sm font-medium text-[var(--text-secondary)]">
              <span>Logout</span>
              <span>⇠</span>
            </button>
          </div>
        </section>
      </div>

      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Application</h2>
        <div className="mt-3 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-subtle)] p-4 text-sm text-[var(--text-secondary)]">
          This application is an educational/research prototype for machine-learning-based risk prediction. It is not a medical diagnostic or treatment tool. Predictions should not be used for clinical decision-making.
        </div>
      </section>
    </div>
  )
}
