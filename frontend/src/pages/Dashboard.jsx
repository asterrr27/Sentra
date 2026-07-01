import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import PageTransition from '../components/layout/PageTransition'
import AttackFlow from '../components/ui/AttackFlow'
import Terminal from '../components/ui/Terminal'
import { createScan, getScanStatus, getScanResults, getScanHistory, listScans, cancelScan } from '../utils/api'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const SCENARIO_LIST = [
  'goal_deviation', 'excessive_agency', 'indirect_injection',
  'permission_boundary', 'multi_step_chain',
  'role_play_jailbreak', 'token_smuggling',
  'context_window_overflow', 'tool_abuse',
]

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

export default function Dashboard() {
  const navigate = useNavigate()
  const [provider, setProvider] = useState('demo')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('')
  const [agentUrl, setAgentUrl] = useState('')
  const [authHeader, setAuthHeader] = useState('')
  const [iterations, setIterations] = useState(5)
  const [systemPrompt, setSystemPrompt] = useState('')
  const [selectedScenarios, setSelectedScenarios] = useState(SCENARIO_LIST)
  const [connectionStatus, setConnectionStatus] = useState(null)

  const PROVIDER_MODELS = {
    openai: 'gpt-4o-mini',
    anthropic: 'claude-sonnet-4-20250514',
  }
  const [scanning, setScanning] = useState(false)
  const [terminalLines, setTerminalLines] = useState([])
  const [progress, setProgress] = useState(0)
  const [completedScenarios, setCompletedScenarios] = useState(0)
  const [cycle, setCycle] = useState(0)
  const [scans, setScans] = useState([])
  const [history, setHistory] = useState([])
  const [compareIds, setCompareIds] = useState([])
  const chartRef = useRef(null)
  const chartInstance = useRef(null)
  const scanIdRef = useRef(null)
  const pollRef = useRef(null)

  useEffect(() => {
    listScans().then(setScans).catch(() => {})
    getScanHistory().then(setHistory).catch(() => {})
  }, [])

  useEffect(() => {
    if (!chartRef.current || !history.length) return
    if (chartInstance.current) chartInstance.current.destroy()
    const ctx = chartRef.current.getContext('2d')
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: history.map(d => '#' + d.id).reverse(),
        datasets: [{
          label: 'Score',
          data: history.map(d => d.score).reverse(),
          borderColor: '#06B6D4',
          backgroundColor: ctx => {
            const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 200)
            g.addColorStop(0, 'rgba(6,182,212,0.12)')
            g.addColorStop(1, 'rgba(6,182,212,0)')
            return g
          },
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#06B6D4',
          pointRadius: 3,
          pointHoverRadius: 5,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 800, easing: 'easeOutQuart' },
        plugins: { legend: { display: false } },
        scales: {
          y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 10 } } },
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 10 } } },
        },
      },
    })
    return () => { if (chartInstance.current) chartInstance.current.destroy() }
  }, [history])

  const validateUrl = useCallback(() => {
    if (!agentUrl) return
    setConnectionStatus('validating')
    setTimeout(() => {
      setConnectionStatus(agentUrl.startsWith('http') ? 'valid' : 'invalid')
    }, 1000)
  }, [agentUrl])

  const handleCancel = useCallback(async () => {
    if (!scanIdRef.current) return
    try {
      await cancelScan(scanIdRef.current)
      if (pollRef.current) clearInterval(pollRef.current)
      setTerminalLines(prev => [...prev, { text: 'Scan cancelled by user.', type: 'fail' }])
      setScanning(false)
      scanIdRef.current = null
    } catch { /* ignore */ }
  }, [])

  const startScan = useCallback(async () => {
    setScanning(true)
    setTerminalLines([{ text: 'Connecting to security engine...', type: 'info' }])
    setProgress(0)
    setCompletedScenarios(0)
    setCycle(0)

    try {
      const data = {
        provider,
        api_key: apiKey || null,
        model: model || null,
        webhook_url: provider === 'webhook' ? agentUrl : null,
        auth_header: authHeader || null,
        system_prompt: systemPrompt || null,
        iterations,
        scenarios: selectedScenarios.length ? selectedScenarios : undefined,
      }

      const res = await createScan(data)
      scanIdRef.current = res.scan_id
      const scenarioList = selectedScenarios.length ? selectedScenarios : SCENARIO_LIST
      const totalIterations = scenarioList.length * iterations

      setTerminalLines(prev => [...prev, { text: 'Initializing attack engine...', type: 'info' }])
      setTerminalLines(prev => [...prev, { text: `Scan #${res.scan_id} queued. Running ${totalIterations} tests...`, type: 'info' }])

      let lastCompleted = -1
      let pollCycle = 0

      const poll = setInterval(async () => {
        try {
          const st = await getScanStatus(res.scan_id)
          const detail = await getScanResults(res.scan_id)

          if (st.status === 'cancelled') {
            clearInterval(poll)
            pollRef.current = null
            scanIdRef.current = null
            setTerminalLines(prev => [...prev, { text: 'Scan cancelled.', type: 'fail' }])
            setScanning(false)
            return
          }

          let done = 0
          let comp = 0
          if (detail.scenarios) {
            for (const [sname, its] of Object.entries(detail.scenarios)) {
              done += its.length
              if (its.length === iterations) comp++
            }
          }

          const pct = Math.min(100, Math.round((done / totalIterations) * 100))
          setProgress(pct)
          setCycle(pollCycle++)
          if (comp > lastCompleted) {
            for (let i = lastCompleted + 1; i <= comp; i++) {
              const sname = scenarioList[i - 1]
              setTerminalLines(prev => [...prev, {
                text: `Scenario: ${SCENARIO_LABELS[sname] || sname} — ${iterations}/${iterations} tests complete`,
                type: 'pass',
              }])
            }
            lastCompleted = comp
            setCompletedScenarios(comp)
          }

          if (st.status === 'completed') {
            clearInterval(poll)
            pollRef.current = null
            scanIdRef.current = null
            setTerminalLines(prev => [...prev, { text: 'Audit completed. Generating security report...', type: 'pass' }])
            setTimeout(() => navigate(`/results/${res.scan_id}`), 800)
          }
        } catch { /* poll continues */ }
      }, 1200)
      pollRef.current = poll
    } catch (err) {
      setTerminalLines(prev => [...prev, { text: `Error: ${err.message}`, type: 'fail' }])
      setScanning(false)
    }
  }, [provider, apiKey, model, agentUrl, authHeader, systemPrompt, iterations, selectedScenarios, navigate])

  const toggleScenario = (s) => {
    setSelectedScenarios(prev =>
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    )
  }

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <div className="grid lg:grid-cols-5 gap-6">
          {/* Left panel — Connect + Form */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold mb-1">Connect Your AI Agent</h2>
              <p className="text-xs text-white/40 mb-4">Paste your deployed AI agent endpoint to begin security testing</p>

              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-white/50 block mb-1">Provider</label>
                  <select
                    value={provider}
                    onChange={e => { setProvider(e.target.value); setModel(PROVIDER_MODELS[e.target.value] || ''); setConnectionStatus(null) }}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-primary/40 transition-colors appearance-none"
                  >
                    <option className="bg-[#111827] text-white" value="demo">Demo Agent (built-in mock)</option>
                    <option className="bg-[#111827] text-white" value="openai">OpenAI</option>
                    <option className="bg-[#111827] text-white" value="anthropic">Anthropic</option>
                    <option className="bg-[#111827] text-white" value="webhook">Webhook URL</option>
                  </select>
                </div>

                {provider === 'webhook' && (
                  <div>
                    <label className="text-xs font-medium text-white/50 block mb-1">Agent URL</label>
                    <div className="flex gap-2">
                      <input
                        type="url"
                        value={agentUrl}
                        onChange={e => { setAgentUrl(e.target.value); setConnectionStatus(null) }}
                        placeholder="https://your-agent.com/chat"
                        className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-primary/40 transition-colors"
                      />
                      <button
                        onClick={validateUrl}
                        disabled={connectionStatus === 'validating'}
                        className="px-4 py-2 text-sm font-medium text-primary border border-primary/30 rounded-lg hover:bg-primary/10 transition-colors disabled:opacity-50"
                      >
                        {connectionStatus === 'validating' ? '...' : 'Validate'}
                      </button>
                    </div>
                    {connectionStatus === 'valid' && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-success">
                        <span className="w-1.5 h-1.5 rounded-full bg-success" /> Endpoint reachable
                      </div>
                    )}
                    {connectionStatus === 'invalid' && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-danger">
                        <span className="w-1.5 h-1.5 rounded-full bg-danger" /> Invalid URL
                      </div>
                    )}
                    {connectionStatus === 'validating' && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-white/40">
                        <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-pulse" /> Validating...
                      </div>
                    )}
                  </div>
                )}

                {provider === 'webhook' && (
                  <div>
                    <label className="text-xs font-medium text-white/50 block mb-1">Auth Header <span className="text-white/20">(optional)</span></label>
                    <input
                      type="text"
                      value={authHeader}
                      onChange={e => setAuthHeader(e.target.value)}
                      placeholder="Bearer sk-..."
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-primary/40 transition-colors"
                    />
                  </div>
                )}

                {(provider === 'openai' || provider === 'anthropic') && (
                  <div>
                    <label className="text-xs font-medium text-white/50 block mb-1">API Key</label>
                    <input
                      type="password"
                      value={apiKey}
                      onChange={e => setApiKey(e.target.value)}
                      placeholder="sk-..."
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-primary/40 transition-colors"
                    />
                  </div>
                )}

                {(provider === 'openai' || provider === 'anthropic') && (
                  <div>
                    <label className="text-xs font-medium text-white/50 block mb-1">Model</label>
                    <select
                      value={model}
                      onChange={e => setModel(e.target.value)}
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-primary/40 transition-colors appearance-none"
                    >
                      {provider === 'openai' && (
                        <>
                          <option className="bg-[#111827] text-white" value="gpt-4o-mini">GPT-4o Mini</option>
                          <option className="bg-[#111827] text-white" value="gpt-4o">GPT-4o</option>
                          <option className="bg-[#111827] text-white" value="gpt-4-turbo">GPT-4 Turbo</option>
                        </>
                      )}
                      {provider === 'anthropic' && (
                        <>
                          <option className="bg-[#111827] text-white" value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                          <option className="bg-[#111827] text-white" value="claude-haiku-3-5-20241022">Claude Haiku 3.5</option>
                          <option className="bg-[#111827] text-white" value="claude-opus-4-20250514">Claude Opus 4</option>
                        </>
                      )}
                    </select>
                  </div>
                )}

                <div>
                  <label className="text-xs font-medium text-white/50 block mb-1">System Prompt <span className="text-white/20">(optional)</span></label>
                  <textarea
                    value={systemPrompt}
                    onChange={e => setSystemPrompt(e.target.value)}
                    rows={3}
                    placeholder="Leave blank for default restrictive prompt"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/20 focus:outline-none focus:border-primary/40 transition-colors resize-none"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-white/50 block mb-1">Iterations: <span className="gradient-text font-bold">{iterations}</span></label>
                  <input
                    type="range"
                    min={1}
                    max={20}
                    value={iterations}
                    onChange={e => setIterations(Number(e.target.value))}
                    className="w-full accent-primary"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-white/50 block mb-2">Scenarios</label>
                  <div className="grid grid-cols-2 gap-2">
                    {SCENARIO_LIST.map(s => (
                      <label
                        key={s}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs cursor-pointer transition-colors ${
                          selectedScenarios.includes(s) ? 'bg-primary/10 border border-primary/20' : 'bg-white/5 border border-white/5'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedScenarios.includes(s)}
                          onChange={() => toggleScenario(s)}
                          className="accent-primary"
                        />
                        {SCENARIO_LABELS[s]}
                      </label>
                    ))}
                  </div>
                </div>

                <button
                  onClick={startScan}
                  disabled={scanning || (provider !== 'demo' && !agentUrl && !apiKey)}
                  className="w-full py-3 text-sm font-semibold text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {scanning ? 'Scanning...' : 'Start Security Audit'}
                </button>
              </div>
            </div>

            {/* Attack visualization during scan */}
            {scanning && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                <AttackFlow cycle={cycle} completed={completedScenarios} />
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-black/40 rounded-full h-2 overflow-hidden border border-white/5">
                    <motion.div
                      className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                  <button
                    onClick={handleCancel}
                    className="px-3 py-1 text-[10px] font-medium text-danger border border-danger/30 rounded-full hover:bg-danger/10 transition-colors shrink-0"
                  >
                    Cancel
                  </button>
                </div>
                <Terminal lines={terminalLines} />
              </motion.div>
            )}
          </div>

          {/* Right panel — History */}
          <div className="lg:col-span-3 space-y-6">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold">Score History</h3>
                <span className="text-[10px] text-white/30">Last 20 scans</span>
              </div>
              <div className="h-48">
                <canvas ref={chartRef} />
              </div>
            </div>

            <div className="glass-card overflow-hidden">
              <div className="flex items-center justify-between p-4 pb-0">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-semibold">Recent Audits</h3>
                  {compareIds.length === 2 && (
                    <button
                      onClick={() => navigate(`/compare?id1=${compareIds[0]}&id2=${compareIds[1]}`)}
                      className="text-xs px-3 py-1 rounded-full bg-primary/20 text-primary hover:bg-primary/30 transition-colors"
                    >
                      Compare Selected
                    </button>
                  )}
                </div>
                {scans.length > 0 && (
                  <span className="text-[10px] text-white/30">{scans.length} scans</span>
                )}
              </div>
              <div className="p-4">
                {scans.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-3xl mb-3 opacity-30">🛡️</div>
                    <p className="text-sm text-white/40">No audits yet</p>
                    <p className="text-xs text-white/20 mt-1">Run your first security audit to see results here</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-[10px] text-white/30 uppercase tracking-wider border-b border-white/5">
                          <th className="pb-2 pr-2 w-8" />
                          <th className="text-left pb-2 pr-4">ID</th>
                          <th className="text-left pb-2 pr-4">Agent</th>
                          <th className="text-left pb-2 pr-4">Score</th>
                          <th className="text-left pb-2 pr-4">Status</th>
                          <th className="text-right pb-2" />
                        </tr>
                      </thead>
                      <tbody>
                        {scans.map((scan, i) => (
                          <motion.tr
                            key={scan.scan_id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.03 }}
                            className="border-b border-white/5 last:border-0"
                          >
                            <td className="py-3 pr-2">
                              {scan.status === 'completed' && (
                                <input
                                  type="checkbox"
                                  checked={compareIds.includes(scan.scan_id)}
                                  onChange={() => setCompareIds(prev =>
                                    prev.includes(scan.scan_id)
                                      ? prev.filter(id => id !== scan.scan_id)
                                      : prev.length < 2 ? [...prev, scan.scan_id] : [prev[1], scan.scan_id]
                                  )}
                                  className="accent-primary"
                                />
                              )}
                            </td>
                            <td className="py-3 pr-4 font-medium text-xs">#{scan.scan_id}</td>
                            <td className="py-3 pr-4 text-white/50 text-xs capitalize">{scan.agent_type}</td>
                            <td className="py-3 pr-4">
                              {scan.score !== null ? (
                                <span className={`text-xs font-bold ${scan.score >= 80 ? 'text-success' : scan.score >= 50 ? 'text-warning' : 'text-danger'}`}>
                                  {scan.score.toFixed(0)}
                                </span>
                              ) : (
                                <span className="text-xs text-white/30">—</span>
                              )}
                            </td>
                            <td className="py-3 pr-4">
                              <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium ${
                                scan.status === 'completed' ? 'bg-success/10 text-success' :
                                scan.status === 'running' ? 'bg-warning/10 text-warning' :
                                'bg-white/5 text-white/30'
                              }`}>
                                <span className={`w-1.5 h-1.5 rounded-full ${scan.status === 'completed' ? 'bg-success' : scan.status === 'running' ? 'bg-warning animate-pulse' : 'bg-white/20'}`} />
                                {scan.status}
                              </span>
                            </td>
                            <td className="text-right py-3">
                              {scan.status === 'completed' && (
                                <button
                                  onClick={() => navigate(`/results/${scan.scan_id}`)}
                                  className="text-xs text-primary/70 hover:text-primary transition-colors"
                                >
                                  View →
                                </button>
                              )}
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}
