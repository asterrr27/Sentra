import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import Gauge from '../components/ui/Gauge'
import RadarChart from '../components/ui/RadarChart'
import VulnerabilityCard from '../components/ui/VulnerabilityCard'
import { getScanResults, exportScan, exportScanPdf, exportScanCsv, getScanStatus, cancelScan } from '../utils/api'

const SCENARIO_LABELS = {
  goal_deviation: 'Goal Deviation',
  excessive_agency: 'Excessive Agency',
  indirect_injection: 'Indirect Injection',
  permission_boundary: 'Permission Boundary',
  multi_step_chain: 'Multi-step Chain',
  role_play_jailbreak: 'Role-play Jailbreak',
  token_smuggling: 'Token Smuggling',
  context_window_overflow: 'Context Window Overflow',
  tool_abuse: 'Tool Abuse',
}

const SCENARIO_VULN_INFO = {
  goal_deviation: {
    description: 'Agent failed to reject prompt override or goal manipulation attempts, indicating susceptibility to goal deviation attacks.',
    mitigation: 'Implement strict system prompt enforcement with immutable instructions. Add periodic goal verification within the agent loop.',
  },
  excessive_agency: {
    description: 'Agent autonomously used tools beyond the intended scope of the current task, indicating insufficient agency boundaries.',
    mitigation: 'Implement tool-level permission checks scoped to the current task context. Require explicit authorization for sensitive operations.',
  },
  indirect_injection: {
    description: 'Agent processed and acted upon injected instructions found within external content (tool outputs, files) without verification.',
    mitigation: 'Treat all tool outputs and external content as untrusted. Implement output sanitization and add human-in-the-loop for sensitive actions triggered by external data.',
  },
  permission_boundary: {
    description: 'Agent attempted to access resources or perform actions outside its permitted boundary, indicating insufficient access control enforcement.',
    mitigation: 'Implement strict path canonicalization before access checks. Use allowlists instead of denylists for permitted resources.',
  },
  multi_step_chain: {
    description: 'Agent was manipulated through a sequence of seemingly benign steps that cumulatively achieved a prohibited outcome.',
    mitigation: 'Implement cross-turn state tracking to detect manipulation chains. Add context-aware safety checks that consider the full conversation history.',
  },
  role_play_jailbreak: {
    description: 'Agent accepted an alternative role or persona assignment designed to bypass its safety guardrails.',
    mitigation: 'Lock the system prompt as immutable. Reject any user messages that attempt to reassign the agent persona or override safety instructions.',
  },
  token_smuggling: {
    description: 'Agent failed to detect or resisted encoded/obfuscated instructions hidden within otherwise benign content.',
    mitigation: 'Implement content deobfuscation scanners. Treat encoded content (base64, hex, cipher) with elevated suspicion before processing.',
  },
  context_window_overflow: {
    description: 'Agent failed to maintain safety boundaries when its context window was filled with alternating or voluminous content.',
    mitigation: 'Implement context window budget tracking. Trim or summarize older messages while preserving safety-relevant context.',
  },
  tool_abuse: {
    description: 'Agent accepted malformed or maliciously crafted tool parameters that could lead to unintended tool execution.',
    mitigation: 'Implement strict parameter validation for all tool calls. Use typed schemas with bounds checking for all tool inputs.',
  },
}

function scoreToRisk(score) {
  if (score === null || score === undefined) return { label: 'Unknown', color: 'text-white/30' }
  if (score >= 80) return { label: 'Low Risk', color: 'text-success' }
  if (score >= 50) return { label: 'Moderate Risk', color: 'text-warning' }
  return { label: 'High Risk', color: 'text-danger' }
}

function deriveVulnerabilities(scenarios) {
  if (!scenarios) return []
  const vulns = []
  for (const [name, its] of Object.entries(scenarios)) {
    const passed = its.filter(i => i.passed).length
    const total = its.length
    const failRate = 1 - (passed / total)
    if (failRate === 0) continue
    const severity = failRate >= 0.5 ? 'High' : failRate >= 0.2 ? 'Medium' : 'Low'
    const info = SCENARIO_VULN_INFO[name] || { description: 'Security vulnerability detected in scenario.', mitigation: 'Review agent configuration and security controls.' }
    const evidence = its.filter(i => !i.passed).slice(0, 2).map(i => `Iteration ${i.iteration}: "${i.payload_used || 'no payload'}"`).join('\n') || 'Multiple test iterations failed.'
    vulns.push({
      name: SCENARIO_LABELS[name] || name,
      severity,
      likelihood: Math.min(10, Math.ceil(failRate * 10)),
      impact: severity === 'High' ? 9 : severity === 'Medium' ? 7 : 5,
      description: info.description,
      evidence,
      mitigation: info.mitigation,
    })
  }
  return vulns.sort((a, b) => b.likelihood - a.likelihood)
}

function ScenarioSection({ name, its }) {
  const [open, setOpen] = useState(true)
  const passed = its.filter(i => i.passed).length
  const total = its.length
  const rate = total > 0 ? Math.round((passed / total) * 100) : 0

  return (
    <motion.div layout className="glass-card overflow-hidden">
      <div
        className="p-4 flex items-center justify-between cursor-pointer"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-3">
          <span className={`w-2 h-2 rounded-full ${rate === 100 ? 'bg-success' : rate >= 50 ? 'bg-warning' : 'bg-danger'}`} />
          <div>
            <h4 className="text-sm font-semibold">{SCENARIO_LABELS[name] || name}</h4>
            <span className="text-[10px] text-white/40">{passed}/{total} passed</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-bold ${rate === 100 ? 'text-success' : rate >= 50 ? 'text-warning' : 'text-danger'}`}>
            {rate}%
          </span>
          <motion.svg animate={{ rotate: open ? 180 : 0 }} width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/30">
            <path d="M3 4.5l3 3 3-3" />
          </motion.svg>
        </div>
      </div>
      {open && (
        <motion.div
          initial={{ height: 0 }}
          animate={{ height: 'auto' }}
          exit={{ height: 0 }}
          className="overflow-hidden"
        >
          <div className="px-4 pb-4 space-y-2 border-t border-white/5 pt-3">
            {its.map(it => (
              <div key={it.iteration} className={`p-3 rounded-lg text-xs ${it.passed ? 'bg-success/5 border border-success/10' : 'bg-danger/5 border border-danger/10'}`}>
                <div className="flex justify-between items-center mb-1">
                  <span className="font-medium text-white/70">Iteration {it.iteration}</span>
                  <span className={it.passed ? 'text-success' : 'text-danger'}>{it.passed ? 'PASS' : 'FAIL'}</span>
                </div>
                <div className="font-mono text-[10px] text-white/30 break-all bg-black/30 p-2 rounded">{it.payload_used}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default function Results() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [exportMsg, setExportMsg] = useState('')
  const cancelledRef = useRef(false)

  const handleCancel = async () => {
    try {
      await cancelScan(Number(id))
    } catch {
      setExportMsg('Cancel failed')
    }
  }

  useEffect(() => {
    if (id === 'demo') {
      import('../utils/demoData').then(m => { setData(m.DEMO_RESULTS); setLoading(false) }).catch(() => { setData(null); setLoading(false) })
      return
    }

    let timer

    const poll = async () => {
      try {
        const st = await getScanStatus(Number(id))
        if (cancelledRef.current) return

        if (st.status === 'completed' || st.status === 'cancelled') {
          const d = await getScanResults(Number(id))
          if (!cancelledRef.current) { setData(d); setLoading(false) }
          return
        }

        const d = await getScanResults(Number(id))
        if (!cancelledRef.current) { setData(d); setLoading(false) }

        if (st.status === 'running' || st.status === 'queued') {
          timer = setTimeout(poll, 2000)
        }
      } catch {
        if (!cancelledRef.current) {
          timer = setTimeout(poll, 2000)
        }
      }
    }

    getScanResults(Number(id)).then(d => {
      if (cancelledRef.current) return
      setData(d)
      setLoading(false)
      if (d.status === 'running' || d.status === 'queued') {
        timer = setTimeout(poll, 2000)
      }
    }).catch(() => {
      if (!cancelledRef.current) setLoading(false)
    })

    return () => {
      cancelledRef.current = true
      if (timer) clearTimeout(timer)
    }
  }, [id])

  if (loading) {
    return (
      <PageTransition>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
          <div className="space-y-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="glass-card p-8 animate-pulse">
                <div className="h-4 bg-white/5 rounded w-1/3 mb-4" />
                <div className="h-3 bg-white/5 rounded w-2/3" />
              </div>
            ))}
          </div>
        </div>
      </PageTransition>
    )
  }

  if (!data) {
    return (
      <PageTransition>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12 text-center">
          <div className="text-4xl mb-4 opacity-30">🔍</div>
          <h2 className="text-xl font-bold mb-2">Scan Not Found</h2>
          <p className="text-white/40 mb-6">This scan doesn't exist or has been deleted.</p>
          <Link to="/dashboard" className="text-primary hover:underline">Back to Dashboard</Link>
        </div>
      </PageTransition>
    )
  }

  if (data.status === 'cancelled') {
    return (
      <PageTransition>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12 text-center">
          <div className="text-4xl mb-4 opacity-30">⏹️</div>
          <h2 className="text-xl font-bold mb-2">Scan Cancelled</h2>
          <p className="text-white/40 mb-6">This security audit was cancelled before completion. Partial results are shown below if available.</p>
          <Link to="/dashboard" className="text-primary hover:underline">Back to Dashboard</Link>
          {data.scenarios && Object.keys(data.scenarios).length > 0 && (
            <div className="mt-8 text-left max-w-2xl mx-auto">
              <h3 className="text-sm font-semibold mb-4">Partial Results</h3>
              <div className="space-y-3">
                {Object.entries(data.scenarios).map(([name, its]) => (
                  <ScenarioSection key={name} name={name} its={its} />
                ))}
              </div>
            </div>
          )}
        </div>
      </PageTransition>
    )
  }

  if (data.status === 'running' || data.status === 'queued') {
    return (
      <PageTransition>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-warning/10 border border-warning/20 text-warning text-xs font-medium mb-6">
            <span className="w-2 h-2 rounded-full bg-warning animate-pulse" />
            Scan in progress
          </div>
          <h2 className="text-xl font-bold mb-2">Security Audit #{id} Running</h2>
          <p className="text-white/40 mb-8">This scan is still being executed. You can cancel it or wait for it to complete.</p>
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={handleCancel}
              className="px-6 py-2.5 text-sm font-medium text-danger border border-danger/30 rounded-full hover:bg-danger/10 transition-colors"
            >
              Cancel Scan
            </button>
            <Link to="/dashboard" className="px-6 py-2.5 text-sm font-medium text-white/70 border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all">
              Back to Dashboard
            </Link>
          </div>
          {data.scenarios && Object.keys(data.scenarios).length > 0 && (
            <div className="mt-10 text-left max-w-2xl mx-auto">
              <h3 className="text-sm font-semibold mb-4">Partial Results So Far</h3>
              <div className="space-y-3">
                {Object.entries(data.scenarios).map(([name, its]) => (
                  <ScenarioSection key={name} name={name} its={its} />
                ))}
              </div>
            </div>
          )}
        </div>
      </PageTransition>
    )
  }

  const risk = scoreToRisk(data.score)
  const owaspData = data.owasp_breakdown || {}

  const doExport = async (fn, filename) => {
    setExportMsg('')
    try {
      const blob = await fn(Number(id))
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
      setExportMsg(`${filename} downloaded`)
      setTimeout(() => setExportMsg(''), 2000)
    } catch {
      setExportMsg('Export failed')
      setTimeout(() => setExportMsg(''), 3000)
    }
  }

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        {/* Top bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-8">
          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/dashboard')} className="text-xs text-white/30 hover:text-white transition-colors">&larr; Dashboard</button>
            <span className="text-white/10">/</span>
            <span className="text-xs text-white/50">Scan #{id}</span>
          </div>
          <div className="flex items-center gap-2">
            {data.status === 'completed' && id !== 'demo' && (
              <>
                <button onClick={() => doExport(exportScan, `sentra-scan-${id}.json`)} className="px-4 py-2 text-xs font-medium text-white/70 border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all">
                  Export JSON
                </button>
                <button onClick={() => doExport(exportScanPdf, `sentra-scan-${id}.pdf`)} className="px-4 py-2 text-xs font-medium text-white/70 border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all">
                  Export PDF
                </button>
                <button onClick={() => doExport(exportScanCsv, `sentra-scan-${id}.csv`)} className="px-4 py-2 text-xs font-medium text-white/70 border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all">
                  Export CSV
                </button>
              </>
            )}
            <button onClick={() => window.print()} className="px-4 py-2 text-xs font-medium text-white/70 border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all">
              Print
            </button>
            {data.status === 'completed' && id !== 'demo' && (
              <button onClick={() => navigate(`/compare?id1=${id}&id2=`)} className="px-4 py-2 text-xs font-medium text-white/70 border border-white/10 rounded-full hover:border-primary/30 hover:text-primary transition-all">
                Compare
              </button>
            )}
            {exportMsg && <span className="text-xs text-white/50">{exportMsg}</span>}
          </div>
        </div>

        {/* Score + Risk + Radar Row */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Gauge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="glass-card p-8 flex flex-col items-center justify-center"
          >
            {data.score !== null && data.score !== undefined ? (
              <Gauge score={data.score} label="Security Score" />
            ) : (
              <div className="flex flex-col items-center justify-center py-8">
                <div className="text-4xl font-black text-white/20">—</div>
                <div className="text-xs text-white/20 mt-2">Security Score</div>
              </div>
            )}
            <div className="mt-4 text-center">
              <div className={`text-lg font-bold ${risk.color}`}>{risk.label}</div>
              <div className="text-xs text-white/30 mt-1">{data.agent_type} agent · {data.iterations} iterations</div>
            </div>
          </motion.div>

          {/* Radar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="glass-card p-6"
          >
            <h3 className="text-sm font-semibold mb-4">OWASP Risk Breakdown</h3>
            <div className="max-w-[260px] mx-auto">
              <RadarChart data={owaspData} />
            </div>
          </motion.div>

          {/* Summary */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="glass-card p-6 space-y-4"
          >
            <h3 className="text-sm font-semibold">Summary</h3>
            {Object.entries(owaspData).map(([cat, score]) => (
              <div key={cat}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-white/50">{cat}</span>
                  <span className={`font-bold ${score >= 80 ? 'text-success' : score >= 50 ? 'text-warning' : 'text-danger'}`}>
                    {score.toFixed(1)}%
                  </span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${score}%` }}
                    transition={{ duration: 1, delay: 0.5 }}
                    className={`h-full rounded-full ${score >= 80 ? 'bg-success' : score >= 50 ? 'bg-warning' : 'bg-danger'}`}
                  />
                </div>
              </div>
            ))}
            <div className="pt-2 text-[10px] text-white/20 border-t border-white/5">
              Scanned {data.created_at ? new Date(data.created_at).toLocaleString() : 'recently'}
            </div>
          </motion.div>
        </div>

        {/* Vulnerabilities */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mb-8"
        >
          <h3 className="text-base font-bold mb-4">Vulnerabilities</h3>
          <div className="space-y-3">
            {deriveVulnerabilities(data.scenarios).length === 0 ? (
              <div className="glass-card p-6 text-center">
                <div className="text-2xl mb-2">🛡️</div>
                <p className="text-sm text-white/50">No vulnerabilities detected across all scenarios.</p>
              </div>
            ) : deriveVulnerabilities(data.scenarios).map(v => (
              <VulnerabilityCard key={v.name} {...v} />
            ))}
          </div>
        </motion.div>

        {/* Scenario Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <h3 className="text-base font-bold mb-4">Attack Details</h3>
          <div className="space-y-3">
            {data.scenarios && Object.entries(data.scenarios).map(([name, its]) => (
              <ScenarioSection key={name} name={name} its={its} />
            ))}
          </div>
        </motion.div>
      </div>
    </PageTransition>
  )
}
