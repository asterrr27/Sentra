import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Link } from 'react-router-dom'
import PageTransition from '../components/layout/PageTransition'
import { getScanResults } from '../utils/api'

export default function Compare() {
  const [searchParams] = useSearchParams()
  const id1 = searchParams.get('id1')
  const id2 = searchParams.get('id2')
  const [data1, setData1] = useState(null)
  const [data2, setData2] = useState(null)

  useEffect(() => {
    if (id1) getScanResults(Number(id1)).then(setData1).catch(() => {})
    if (id2) getScanResults(Number(id2)).then(setData2).catch(() => {})
  }, [id1, id2])

  const Card = ({ data, label }) => {
    if (!data) return (
      <div className="glass-card p-8 text-center">
        <p className="text-sm text-white/30">Paste a scan ID to compare</p>
      </div>
    )
    const score = data.score || 0
    return (
      <div className={`glass-card p-6 ${score >= 80 ? 'ring-1 ring-success/20' : score >= 50 ? 'ring-1 ring-warning/20' : 'ring-1 ring-danger/20'}`}>
        <div className="text-center mb-6">
          <div className="text-xs text-white/30 mb-1">{label}</div>
          <div className={`text-4xl font-black ${score >= 80 ? 'text-success' : score >= 50 ? 'text-warning' : 'text-danger'}`}
            style={{ textShadow: score >= 80 ? '0 0 20px rgba(34,197,94,0.3)' : score >= 50 ? '0 0 20px rgba(245,158,11,0.3)' : '0 0 20px rgba(239,68,68,0.3)' }}>
            {score.toFixed(0)}
          </div>
          <div className="text-xs text-white/30 mt-1">Security Score</div>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[10px] text-white/30 uppercase tracking-wider border-b border-white/5">
              <th className="text-left pb-2">Scenario</th>
              <th className="text-right pb-2">Pass Rate</th>
            </tr>
          </thead>
          <tbody>
            {data.scenarios && Object.entries(data.scenarios).map(([name, its]) => {
              const passed = its.filter(i => i.passed).length
              const total = its.length
              const rate = Math.round((passed / total) * 100)
              return (
                <tr key={name} className="border-b border-white/5 last:border-0">
                  <td className="py-2 text-xs text-white/50 capitalize">{name.replace(/_/g, ' ')}</td>
                  <td className={`py-2 text-xs text-right font-bold ${rate >= 80 ? 'text-success' : rate >= 50 ? 'text-warning' : 'text-danger'}`}>
                    {passed}/{total}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <Link to={`/results/${data.scan_id}`} className="mt-4 block text-center text-xs text-primary/60 hover:text-primary transition-colors">
          View Full Report →
        </Link>
      </div>
    )
  }

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-xl font-bold">Compare Scans</h1>
          <Link to="/dashboard" className="text-xs text-white/30 hover:text-white transition-colors">&larr; Dashboard</Link>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <Card data={data1} label={id1 ? `Scan #${id1}` : 'Scan 1'} />
          <Card data={data2} label={id2 ? `Scan #${id2}` : 'Scan 2'} />
        </div>
        {!id1 && !id2 && (
          <div className="text-center mt-12">
            <div className="text-3xl mb-3 opacity-30">📊</div>
            <p className="text-sm text-white/40">Select two scans to compare their results side by side</p>
            <Link to="/dashboard" className="inline-block mt-4 text-sm text-primary hover:underline">
              Go to Dashboard
            </Link>
          </div>
        )}
      </div>
    </PageTransition>
  )
}
