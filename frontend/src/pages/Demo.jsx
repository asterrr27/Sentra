import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import AttackFlow from '../components/ui/AttackFlow'
import Terminal from '../components/ui/Terminal'
import { useNavigate } from 'react-router-dom'

const DEMO_LINES = [
  { text: 'Connecting to demo security engine...', type: 'info' },
  { text: 'Initializing attack simulation environment...', type: 'info' },
  { text: 'Launching Goal Deviation attack (1/13)...', type: 'info' },
  { text: 'Testing prompt override resistance...', type: 'info' },
  { text: 'Goal Deviation: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Excessive Agency attack (2/13)...', type: 'info' },
  { text: 'Testing autonomous tool execution boundaries...', type: 'info' },
  { text: 'Excessive Agency: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Indirect Injection attack (3/13)...', type: 'info' },
  { text: 'Testing tool output poisoning resistance...', type: 'info' },
  { text: 'Indirect Injection: 3/5 tests passed', type: 'pass' },
  { text: 'Launching Permission Boundary attack (4/13)...', type: 'info' },
  { text: 'Testing path traversal and boundary enforcement...', type: 'info' },
  { text: 'Permission Boundary: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Multi-step Chain attack (5/13)...', type: 'info' },
  { text: 'Testing multi-step manipulation chains...', type: 'info' },
  { text: 'Multi-step Chain: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Role-play Jailbreak attack (6/13)...', type: 'info' },
  { text: 'Testing role-based safety override resistance...', type: 'info' },
  { text: 'Role-play Jailbreak: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Token Smuggling attack (7/13)...', type: 'info' },
  { text: 'Testing encoded instruction detection...', type: 'info' },
  { text: 'Token Smuggling: 3/5 tests passed', type: 'pass' },
  { text: 'Launching Context Window Overflow attack (8/13)...', type: 'info' },
  { text: 'Testing context boundary enforcement...', type: 'info' },
  { text: 'Context Window Overflow: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Tool Abuse attack (9/13)...', type: 'info' },
  { text: 'Testing tool parameter constraint enforcement...', type: 'info' },
  { text: 'Tool Abuse: 4/5 tests passed', type: 'pass' },
  { text: 'Launching System Prompt Extraction attack (10/13)...', type: 'info' },
  { text: 'Testing system prompt disclosure resistance...', type: 'info' },
  { text: 'System Prompt Extraction: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Tool Output Injection attack (11/13)...', type: 'info' },
  { text: 'Testing untrusted tool output handling...', type: 'info' },
  { text: 'Tool Output Injection: 3/5 tests passed', type: 'pass' },
  { text: 'Launching Prompt Boundary Probing attack (12/13)...', type: 'info' },
  { text: 'Testing config and schema leakage resistance...', type: 'info' },
  { text: 'Prompt Boundary Probing: 4/5 tests passed', type: 'pass' },
  { text: 'Launching Tool Loop Exploit attack (13/13)...', type: 'info' },
  { text: 'Testing unbounded action chain resistance...', type: 'info' },
  { text: 'Tool Loop Exploit: 2/5 tests passed', type: 'pass' },
  { text: 'Collecting metrics and generating report...', type: 'info' },
  { text: 'Audit completed. Security score: 76/100', type: 'pass' },
  { text: 'Redirecting to results...', type: 'info' },
]

export default function Demo() {
  const navigate = useNavigate()
  const [started, setStarted] = useState(false)
  const [paused, setPaused] = useState(false)
  const [lines, setLines] = useState([])
  const [completed, setCompleted] = useState(0)
  const [cycle, setCycle] = useState(0)
  const [progress, setProgress] = useState(0)
  const indexRef = useRef(0)

  const timeoutRef = useRef(null)

  useEffect(() => {
    if (!started || paused) return
    let unmounted = false

    const lineInterval = setInterval(() => {
      if (unmounted) return
      const i = indexRef.current
      if (i < DEMO_LINES.length) {
        setLines(prev => [...prev, DEMO_LINES[i]])
        if (DEMO_LINES[i].type === 'pass') {
          setCompleted(prev => Math.min(prev + 1, 13))
        }
        setProgress(Math.min(100, Math.round(((i + 1) / DEMO_LINES.length) * 100)))
        indexRef.current = i + 1
      } else {
        clearInterval(lineInterval)
        timeoutRef.current = setTimeout(() => { if (!unmounted) navigate('/results/demo') }, 500)
      }
    }, 220)

    const cycleInterval = setInterval(() => {
      if (unmounted) return
      setCycle(c => c + 1)
    }, 180)

    return () => {
      unmounted = true
      clearInterval(lineInterval)
      clearInterval(cycleInterval)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [started, paused, navigate])

  return (
    <PageTransition>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/5 border border-primary/20 text-primary text-xs font-medium mb-4">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Demo Mode
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold mb-2">Experience Sentra in Action</h1>
          <p className="text-sm text-white/40 max-w-md mx-auto">
            Watch a simulated security audit in real-time. No AI agent needed.
          </p>
        </motion.div>

        {!started ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-10 max-w-md mx-auto"
          >
            <div className="text-4xl mb-4">🎮</div>
            <h3 className="text-base font-semibold mb-2">Demo Security Audit</h3>
            <p className="text-xs text-white/40 mb-6">
              This will run a simulated scan against all 13 attack scenarios spanning 6 OWASP categories and generate a sample security report.
            </p>
            <button
              onClick={() => setStarted(true)}
              className="w-full py-3 text-sm font-semibold text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all"
            >
              Start Demo Audit
            </button>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4 text-left"
          >
            <AttackFlow cycle={cycle} completed={completed} />
            <div className="bg-black/40 rounded-full h-2 overflow-hidden border border-white/5">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <Terminal lines={lines} />
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setPaused(p => !p)}
                className="px-5 py-2 text-xs font-medium border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all text-white/50"
              >
                {paused ? '▶ Resume' : '⏸ Pause'}
              </button>
              <button
                onClick={() => navigate('/results/demo')}
                className="px-5 py-2 text-xs font-medium border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all text-white/50"
              >
                Skip to Results →
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </PageTransition>
  )
}
