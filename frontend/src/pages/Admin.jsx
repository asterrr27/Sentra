import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import api from '../utils/api'

export default function Admin() {
  const [tab, setTab] = useState('stats')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.get('/admin/stats').then(r => setStats(r.data)).catch(() => {}),
      api.get('/admin/users').then(r => setUsers(r.data)).catch(() => {}),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <PageTransition>
      <div className="max-w-4xl mx-auto px-4 pt-24 text-center text-white/30">Loading...</div>
    </PageTransition>
  )

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <h1 className="text-xl font-bold mb-6">Admin Panel</h1>

        <div className="flex gap-2 mb-6">
          <button onClick={() => setTab('stats')} className={`px-4 py-2 text-sm rounded-lg ${tab === 'stats' ? 'bg-primary/20 text-primary' : 'text-white/50 hover:text-white'}`}>Stats</button>
          <button onClick={() => setTab('users')} className={`px-4 py-2 text-sm rounded-lg ${tab === 'users' ? 'bg-primary/20 text-primary' : 'text-white/50 hover:text-white'}`}>Users</button>
        </div>

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
          <div className="glass-card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-white/30 uppercase tracking-wider border-b border-white/5">
                  <th className="text-left px-4 py-3">ID</th>
                  <th className="text-left px-4 py-3">Username</th>
                  <th className="text-left px-4 py-3">Email</th>
                  <th className="text-left px-4 py-3">Role</th>
                  <th className="text-left px-4 py-3">Created</th>
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
