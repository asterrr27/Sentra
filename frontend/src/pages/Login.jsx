import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <PageTransition>
      <div className="min-h-screen flex items-center justify-center px-4 pt-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-sm glass-card p-8"
        >
          <div className="text-center mb-6">
            <h1 className="text-xl font-bold">Welcome back</h1>
            <p className="text-sm text-white/40 mt-1">Sign in to your Sentra account</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-white/40 block mb-1">Username</label>
              <input
                value={username} onChange={e => setUsername(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-primary/50"
                placeholder="your_username"
                required
              />
            </div>
            <div>
              <label className="text-xs text-white/40 block mb-1">Password</label>
              <input
                type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-primary/50"
                placeholder="••••••••"
                required
              />
            </div>
            {error && <p className="text-xs text-danger">{error}</p>}
            <div className="flex justify-end">
              <Link to="/dashboard" className="text-xs text-white/30 hover:text-primary transition-colors">
                Forgot password?
              </Link>
            </div>
            <button
              type="submit" disabled={busy}
              className="w-full py-2.5 text-sm font-semibold text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all disabled:opacity-50"
            >
              {busy ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
          <p className="text-xs text-white/30 text-center mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline">Register</Link>
          </p>
        </motion.div>
      </div>
    </PageTransition>
  )
}
