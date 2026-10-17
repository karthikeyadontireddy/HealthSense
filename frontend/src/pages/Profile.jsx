import { useEffect, useState } from 'react'
import { apiRequest } from '../utils/api'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { token } = useAuth()
  const [profile, setProfile] = useState(null)
  const [formState, setFormState] = useState({
    age: '',
    gender: '',
    height: '',
    weight: '',
    smoking: '',
    alcohol: '',
    activity: '',
    family_history: '',
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadProfile() {
      setError('')
      try {
        const profileData = await apiRequest('/profile', token)
        setProfile(profileData)
        setFormState({
          age: profileData.age ?? '',
          gender: profileData.gender ?? '',
          height: profileData.height ?? '',
          weight: profileData.weight ?? '',
          smoking: profileData.smoking ?? '',
          alcohol: profileData.alcohol ?? '',
          activity: profileData.activity ?? '',
          family_history: profileData.family_history ?? '',
        })
      } catch (err) {
        setError(err.message)
      }
    }
    loadProfile()
  }, [token])

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormState((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setMessage('')
    try {
      await apiRequest('/profile', token, {
        method: 'PUT',
        body: JSON.stringify(formState),
      })
      setMessage('Profile updated successfully.')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <h1 className="mb-2 text-2xl font-semibold text-[var(--text-primary)]">Patient Profile</h1>
        <p className="text-sm text-[var(--text-secondary)]">Store profile details for reference. Each assessment uses only the features listed for its saved model.</p>
      </section>
      <section className="rounded-3xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-[var(--shadow-soft)]">
        <form className="grid gap-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Age</span>
              <input name="age" type="number" value={formState.age} onChange={handleChange} className="mt-0 w-full" />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Gender</span>
              <select name="gender" value={formState.gender} onChange={handleChange} className="mt-0 w-full">
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Height (cm)</span>
              <input name="height" type="number" value={formState.height} onChange={handleChange} className="mt-0 w-full" />
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Weight (kg)</span>
              <input name="weight" type="number" value={formState.weight} onChange={handleChange} className="mt-0 w-full" />
            </label>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Smoking</span>
              <select name="smoking" value={formState.smoking} onChange={handleChange} className="mt-0 w-full">
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Alcohol</span>
              <select name="alcohol" value={formState.alcohol} onChange={handleChange} className="mt-0 w-full">
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Physical Activity</span>
              <select name="activity" value={formState.activity} onChange={handleChange} className="mt-0 w-full">
                <option value="">Select</option>
                <option value="Low">Low</option>
                <option value="Moderate">Moderate</option>
                <option value="High">High</option>
              </select>
            </label>
            <label>
              <span className="mb-2 block text-sm font-medium text-[var(--text-secondary)]">Family History</span>
              <select name="family_history" value={formState.family_history} onChange={handleChange} className="mt-0 w-full">
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </label>
          </div>
          {message && <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">{message}</div>}
          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <button type="submit" className="w-full rounded-xl bg-[var(--brand)] py-3 text-base font-semibold text-white">Save profile</button>
        </form>
      </section>
    </div>
  )
}
