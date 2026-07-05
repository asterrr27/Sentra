import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { setOnUnauthorized } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const mountedRef = useRef(true)
  const navigate = useNavigate()

  useEffect(() => {
    setOnUnauthorized(() => {
      setUser(null)
      navigate('/login', { replace: true })
    })
  }, [navigate])

  useEffect(() => {
    const token = localStorage.getItem('sentra_token')
    if (!token) { setLoading(false); return }
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    api.get('/auth/me').then(r => {
      if (mountedRef.current) setUser(r.data)
    }).catch(() => {
      if (mountedRef.current) {
        localStorage.removeItem('sentra_token')
        delete api.defaults.headers.common['Authorization']
      }
    }).finally(() => {
      if (mountedRef.current) setLoading(false)
    })
    return () => { mountedRef.current = false }
  }, [])

  const login = useCallback(async (username, password) => {
    const r = await api.post('/auth/login', { username, password })
    localStorage.setItem('sentra_token', r.data.access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${r.data.access_token}`
    setUser(r.data.user)
    return r.data.user
  }, [])

  const register = useCallback(async (username, email, password) => {
    const r = await api.post('/auth/register', { username, email, password })
    localStorage.setItem('sentra_token', r.data.access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${r.data.access_token}`
    setUser(r.data.user)
    return r.data.user
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('sentra_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    navigate('/login', { replace: true })
  }, [navigate])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
