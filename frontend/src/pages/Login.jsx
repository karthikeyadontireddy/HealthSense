import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiRequest } from '../utils/api'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('demo123')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      const data = await apiRequest('/login', null, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      login(data.access_token, { name: email.split('@')[0] || 'User' })
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg-page)] px-4 py-10 text-[var(--text-primary)]">
      <div className="mx-auto max-w-md rounded-[28px] border border-[var(--border-color)] bg-[var(--bg-surface)] p-7 shadow-[var(--shadow-soft)] sm:p-8">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--brand-soft)] text-2xl font-bold text-[var(--brand)]">H</div>
          <h1 className="text-3xl font-semibold tracking-tight">Login</h1>
        </div>

        <p className="mb-6 text-center text-sm leading-6 text-[var(--text-secondary)]">
          This application is an educational/research prototype for machine-learning-based risk prediction. It is not a medical diagnostic or treatment tool.
        </p>
        <div className="mb-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-subtle)] px-3 py-2 text-center text-xs text-[var(--text-secondary)]">
          Demo login: <span className="font-semibold text-[var(--text-primary)]">demo@example.com</span> / <span className="font-semibold text-[var(--text-primary)]">demo123</span>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Email</span>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required className="mt-0 w-full" placeholder="name@example.com" />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Password</span>
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required className="mt-0 w-full" placeholder="••••••••" />
          </label>

          {error && <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

          <button type="submit" className="w-full rounded-xl bg-[var(--brand)] px-4 py-3 text-base font-semibold text-white shadow-sm transition hover:opacity-95">Sign in</button>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--text-secondary)]">
          New user?{' '}
          <Link to="/register" className="font-semibold text-[var(--brand)] underline-offset-4 hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  )
}
