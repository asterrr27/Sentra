import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import { getAllPayloads } from '../utils/api'

const ICONS = {
  goal_deviation: '🎯',
  excessive_agency: '⚡',
  indirect_injection: '🪤',
  permission_boundary: '🔒',
  multi_step_chain: '🔗',
  role_play_jailbreak: '🎭',
  token_smuggling: '📦',
  context_window_overflow: '🌊',
  tool_abuse: '🔧',
  system_prompt_extraction: '🤫',
  tool_output_injection: '📄',
  prompt_boundary_probing: '🔍',
  tool_loop_exploit: '♾️',
}

export default function Payloads() {
  const [payloads, setPayloads] = useState({})
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(null)

  useEffect(() => {
    getAllPayloads().then(r => { setPayloads(r); setError('') }).catch(() => setError('Failed to load payloads'))
  }, [])

  const copyPayload = async (text, key) => {
    const str = typeof text === 'string' ? text : JSON.stringify(text, null, 2)
    try {
      await navigator.clipboard.writeText(str)
    } catch {
      const ta = document.createElement('textarea')
      ta.value = str
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  const entries = Object.entries(payloads)

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-xl font-bold gradient-text">Attack Payload Library</h1>
            <p className="text-xs text-white/40 mt-1">{entries.length} scenario categories</p>
          </div>
          <Link to="/dashboard" className="text-xs text-white/30 hover:text-white transition-colors">&larr; Dashboard</Link>
        </div>

        {error ? (
          <div className="text-center py-16">
            <div className="text-3xl mb-3 opacity-30">⚠️</div>
            <p className="text-sm text-danger">{error}</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-3xl mb-3 opacity-30">📚</div>
            <p className="text-sm text-white/40">No payloads available.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {entries.map(([scenario, payloadList], i) => (
              <motion.div
                key={scenario}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="glass-card overflow-hidden"
              >
                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{ICONS[scenario] || '📋'}</span>
                    <h3 className="text-sm font-semibold capitalize">{scenario.replace(/_/g, ' ')}</h3>
                  </div>
                  <span className="text-[10px] text-white/30">{payloadList.length} payloads</span>
                </div>
                <div className="divide-y divide-white/5">
                  {payloadList.map((payload, j) => (
                    <div key={`${scenario}-${j}`} className="p-4 flex items-start gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="font-mono text-[11px] text-white/60 bg-black/30 rounded-lg p-3 break-all leading-relaxed">
                          {typeof payload === 'string' ? payload : (
                            payload.steps ? payload.steps.map((s, k) => <div key={`${scenario}-${j}-${k}`}>📌 {s}</div>) : JSON.stringify(payload)
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => copyPayload(payload, `${scenario}-${j}`)}
                        className="shrink-0 px-3 py-1.5 text-[10px] font-medium text-white/50 border border-white/10 rounded-lg hover:border-primary/30 hover:text-primary transition-all"
                      >
                        {copied === `${scenario}-${j}` ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </PageTransition>
  )
}
