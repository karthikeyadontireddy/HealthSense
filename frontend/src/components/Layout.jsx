import { useMemo, useState } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const sidebarItems = [
  { label: 'Dashboard', to: '/dashboard', icon: '⌂' },
  { label: 'Disease Assessment', to: '/assessment/diabetes', icon: '↗' },
  { label: 'Model & Research', to: '/research', icon: '◈' },
  { label: 'Health Profile', to: '/profile', icon: '◌' },
  { label: 'Prediction History', to: '/history', icon: '▣' },
  { label: 'Settings', to: '/settings', icon: '⚙' },
]

const analyticsItems = [
  { label: 'Risk Trends', to: '/dashboard', icon: '◔' },
  { label: 'Health Metrics', to: '/dashboard', icon: '◍' },
]

function classNames(...values) {
  return values.filter(Boolean).join(' ')
}

export default function Layout({ children }) {
  const { token, user, logout } = useAuth()
  const { theme, setTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const pageTitle = useMemo(() => {
    const map = {
      '/dashboard': 'Overview',
      '/profile': 'Health Profile',
      '/assessment/diabetes': 'Diabetes Assessment',
      '/history': 'Prediction History',
      '/settings': 'Settings',
      '/result': 'Research Result',
      '/research': 'Model & Research',
    }
    return map[location.pathname] || 'HealthSense'
  }, [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/login')
    setMobileOpen(false)
  }

  return (
    <div className="min-h-screen bg-[var(--bg-page)] text-[var(--text-primary)]">
      <div className="flex min-h-screen">
        <aside
          className={classNames(
            'fixed inset-y-0 left-0 z-40 flex flex-col border-r border-[var(--border-color)] bg-[var(--bg-surface)]/95 backdrop-blur-xl transition-all duration-300 md:static',
            mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
            'w-72 md:w-72'
          )}
        >
          <div className="flex items-center justify-between border-b border-[var(--border-color)] px-5 py-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--brand-soft)] text-sm font-bold text-[var(--brand)]">H</div>
              <div>
                <p className="text-lg font-semibold">HealthSense</p>
              </div>
            </div>
            <button
              className="rounded-lg border border-[var(--border-color)] bg-transparent px-2 py-1 text-xs text-[var(--text-secondary)] md:hidden"
              onClick={() => setMobileOpen(false)}
              aria-label="Close navigation"
            >
              ✕
            </button>
          </div>

          <div className="flex-1 space-y-6 px-4 py-6">
            <div>
              <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">Overview</p>
              <nav className="space-y-1.5">
                {sidebarItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      classNames(
                        'flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition',
                        isActive
                          ? 'bg-[var(--brand-soft)] text-[var(--brand)] shadow-sm'
                          : 'text-[var(--text-secondary)] hover:bg-[var(--bg-subtle)]'
                      )
                    }
                    onClick={() => setMobileOpen(false)}
                  >
                    <span className="inline-flex h-7 w-7 items-center justify-center rounded-xl bg-[var(--bg-subtle)] text-xs">{item.icon}</span>
                    {item.label}
                  </NavLink>
                ))}
              </nav>
            </div>

            <div>
              <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">Analytics</p>
              <nav className="space-y-1.5">
                {analyticsItems.map((item) => (
                  <NavLink
                    key={item.to + item.label}
                    to={item.to}
                    className={({ isActive }) =>
                      classNames(
                        'flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition',
                        isActive
                          ? 'bg-[var(--brand-soft)] text-[var(--brand)]'
                          : 'text-[var(--text-secondary)] hover:bg-[var(--bg-subtle)]'
                      )
                    }
                    onClick={() => setMobileOpen(false)}
                  >
                    <span className="inline-flex h-7 w-7 items-center justify-center rounded-xl bg-[var(--bg-subtle)] text-xs">{item.icon}</span>
                    {item.label}
                  </NavLink>
                ))}
              </nav>
            </div>
          </div>

          <div className="border-t border-[var(--border-color)] p-4">
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-2xl border border-[var(--border-color)] bg-transparent px-3 py-2.5 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-subtle)]"
            >
              <span className="inline-flex h-7 w-7 items-center justify-center rounded-xl bg-[var(--bg-subtle)]">⇠</span>
              Logout
            </button>
          </div>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-[var(--border-color)] bg-[var(--bg-surface)]/90 backdrop-blur-xl">
            <div className="flex items-center justify-between px-4 py-4 md:px-6">
              <div className="flex items-center gap-3">
                <button
                  className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--border-color)] bg-[var(--bg-subtle)] text-lg text-[var(--text-primary)] md:hidden"
                  onClick={() => setMobileOpen(true)}
                  aria-label="Open navigation"
                >
                  ☰
                </button>
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">Research prototype</p>
                  <h1 className="text-xl font-semibold text-[var(--text-primary)]">{pageTitle}</h1>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  aria-label="Toggle color mode"
                  onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                  className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--border-color)] bg-[var(--bg-subtle)] text-lg text-[var(--text-primary)]"
                >
                  {theme === 'dark' ? '☀' : '☾'}
                </button>

                <button className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--border-color)] bg-[var(--bg-subtle)] text-lg text-[var(--text-primary)]" aria-label="Notifications">
                  ⍰
                </button>

                <Link to="/profile" className="flex items-center gap-3 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-subtle)] px-2 py-1.5">
                  <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--brand-soft)] font-semibold text-[var(--brand)]">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                  <div className="hidden text-left sm:block">
                    <p className="text-sm font-medium text-[var(--text-primary)]">{user?.name || 'User'}</p>
                    <p className="text-[11px] text-[var(--text-muted)]">Research user</p>
                  </div>
                </Link>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 md:px-6 lg:px-8">
            {children}
          </main>
        </div>
      </div>

      {mobileOpen && (
        <button
          aria-label="Close navigation overlay"
          className="fixed inset-0 z-30 bg-slate-950/40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}
    </div>
  )
}
