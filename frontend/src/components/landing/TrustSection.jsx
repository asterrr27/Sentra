import { useRef } from 'react'
import { useInView } from 'framer-motion'
import StatCounter from '../ui/StatCounter'

const STATS = [
  { value: 13, suffix: '', label: 'Attack Scenarios' },
  { value: 65, suffix: '+', label: 'Attack Payloads' },
  { value: 3, suffix: '', label: 'Agent Connectors' },
  { value: 100, suffix: '%', label: 'OWASP-Aligned' },
]

export default function TrustSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section ref={ref} className="py-20 border-y border-white/5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold mb-3">Built for Security Teams</h2>
          <p className="text-white/40 max-w-lg mx-auto">Comprehensive AI agent security testing aligned with OWASP standards</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {STATS.map(stat => (
            <StatCounter key={stat.label} {...stat} />
          ))}
        </div>
      </div>
    </section>
  )
}
