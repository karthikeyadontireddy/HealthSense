import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('healthsense-token'))
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('healthsense-user')
    return stored ? JSON.parse(stored) : { name: 'User' }
  })

  useEffect(() => {
    if (token) {
      localStorage.setItem('healthsense-token', token)
    } else {
      localStorage.removeItem('healthsense-token')
    }
  }, [token])

  useEffect(() => {
    if (user) {
      localStorage.setItem('healthsense-user', JSON.stringify(user))
    } else {
      localStorage.removeItem('healthsense-user')
    }
  }, [user])

  const login = (authToken, authUser = null) => {
    setToken(authToken)
    const fallbackUser = authUser ?? { name: 'User' }
    setUser(fallbackUser)
  }

  const logout = () => {
    setToken(null)
    setUser({ name: 'User' })
  }

  return <AuthContext.Provider value={{ token, user, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
