import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import { useAuth } from '../context/AuthContext'
import api, { resetUserPassword } from '../utils/api'

export default function Admin() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [tab, setTab] = useState('stats')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [adminError, setAdminError] = useState('')
  const [resetUserId, setResetUserId] = useState(null)
  const [resetPasswords, setResetPasswords] = useState({})
  const [resetMsg, setResetMsg] = useState({})

  useEffect(() => {
    if (user && user.role !== 'admin') {
      navigate('/dashboard', { replace: true })
      return
    }
    setLoading(true)
    setAdminError('')
    Promise.all([
      api.get('/admin/stats').then(r => setStats(r.data)).catch(() => setAdminError('Failed to load stats')),
      api.get('/admin/users').then(r => setUsers(r.data)).catch(() => setAdminError('Failed to load users')),
    ]).finally(() => setLoading(false))
  }, [user, navigate])

  if (loading) {
    return (
      <PageTransition>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
          <div className="h-7 bg-white/5 rounded w-32 mb-6 animate-pulse" />
          <div className="flex gap-2 mb-6">
            <div className="h-9 w-16 bg-white/5 rounded-lg animate-pulse" />
            <div className="h-9 w-16 bg-white/5 rounded-lg animate-pulse" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="glass-card p-5 animate-pulse">
                <div className="h-8 w-16 bg-white/5 rounded mx-auto mb-2" />
                <div className="h-3 w-20 bg-white/5 rounded mx-auto" />
              </div>
            ))}
          </div>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <h1 className="text-xl font-bold mb-6">Admin Panel</h1>

        <div className="flex gap-2 mb-6">
          <button onClick={() => setTab('stats')} className={`px-4 py-2 text-sm rounded-lg ${tab === 'stats' ? 'bg-primary/20 text-primary' : 'text-white/50 hover:text-white'}`}>Stats</button>
          <button onClick={() => setTab('users')} className={`px-4 py-2 text-sm rounded-lg ${tab === 'users' ? 'bg-primary/20 text-primary' : 'text-white/50 hover:text-white'}`}>Users</button>
        </div>

        {adminError && (
          <div className="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-lg text-sm text-danger text-center">
            {adminError}
          </div>
        )}
        {tab === 'stats' && stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Users', value: stats.total_users },
              { label: 'Total Scans', value: stats.total_scans },
              { label: 'Completed', value: stats.completed_scans },
              { label: 'Avg Score', value: stats.average_score },
            ].map(s => (
              <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 text-center">
                <div className="text-2xl font-black gradient-text">{s.value}</div>
                <div className="text-xs text-white/30 mt-1">{s.label}</div>
              </motion.div>
            ))}
          </div>
        )}

        {tab === 'users' && (
          <div className="glass-card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-white/30 uppercase tracking-wider border-b border-white/5">
                  <th className="text-left px-4 py-3">ID</th>
                  <th className="text-left px-4 py-3">Username</th>
                  <th className="text-left px-4 py-3">Email</th>
                  <th className="text-left px-4 py-3">Role</th>
                  <th className="text-left px-4 py-3">Created</th>
                  <th className="text-left px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b border-white/5 last:border-0 hover:bg-white/5">
                    <td className="px-4 py-3 text-white/50">{u.id}</td>
                    <td className="px-4 py-3">{u.username}</td>
                    <td className="px-4 py-3 text-white/50">{u.email}</td>
                    <td className="px-4 py-3"><span className={`text-xs px-2 py-0.5 rounded-full ${u.role === 'admin' ? 'bg-primary/20 text-primary' : 'bg-white/5 text-white/50'}`}>{u.role}</span></td>
                    <td className="px-4 py-3 text-white/30 text-xs">{u.created_at?.split('T')[0] || '-'}</td>
                    <td className="px-4 py-3">
                      {resetUserId === u.id ? (
                        <div className="flex items-center gap-1">
                          <input
                            type="password"
                            value={resetPasswords[u.id] || ''}
                            onChange={e => setResetPasswords(p => ({...p, [u.id]: e.target.value}))}
                            placeholder="New password"
                            className="w-24 bg-white/5 border border-white/10 rounded px-2 py-1 text-[10px] text-white placeholder-white/20 focus:outline-none focus:border-primary/40"
                          />
                          <button
                            onClick={async () => {
                              const pw = resetPasswords[u.id]
                              if (!pw) return
                              try {
                                await resetUserPassword(u.id, pw)
                                setResetMsg(p => ({...p, [u.id]: 'Done!'}))
                              } catch { setResetMsg(p => ({...p, [u.id]: 'Failed'})) }
                              setTimeout(() => {
                                setResetMsg(p => ({...p, [u.id]: null}))
                                setResetUserId(null)
                                setResetPasswords(p => { const n = {...p}; delete n[u.id]; return n })
                              }, 2000)
                            }}
                            className="text-[10px] px-2 py-1 rounded bg-primary/20 text-primary hover:bg-primary/30"
                          >Set</button>
                          <button onClick={() => { setResetUserId(null); setResetPasswords(p => { const n = {...p}; delete n[u.id]; return n }) }} className="text-[10px] px-2 py-1 text-white/30 hover:text-white">✕</button>
                        </div>
                      ) : (
                        <button
                          onClick={() => { setResetUserId(u.id); setResetMsg(p => ({...p, [u.id]: null})) }}
                          className="text-[10px] text-white/30 hover:text-primary transition-colors"
                        >{resetMsg[u.id] || 'Reset PW'}</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </PageTransition>
  )
}
