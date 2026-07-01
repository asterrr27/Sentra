import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await register(username, email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed')
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
            <h1 className="text-xl font-bold">Create account</h1>
            <p className="text-sm text-white/40 mt-1">Get started with Sentra</p>
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
              <label className="text-xs text-white/40 block mb-1">Email</label>
              <input
                type="email" value={email} onChange={e => setEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-primary/50"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="text-xs text-white/40 block mb-1">Password</label>
              <input
                type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-primary/50"
                placeholder="minimum 8 characters"
                minLength={8}
                required
              />
            </div>
            {error && <p className="text-xs text-danger">{error}</p>}
            <button
              type="submit" disabled={busy}
              className="w-full py-2.5 text-sm font-semibold text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all disabled:opacity-50"
            >
              {busy ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
          <p className="text-xs text-white/30 text-center mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline">Sign in</Link>
          </p>
        </motion.div>
      </div>
    </PageTransition>
  )
}
