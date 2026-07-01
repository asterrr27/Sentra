import { useRef } from 'react'
import { useInView } from 'framer-motion'
import StatCounter from '../ui/StatCounter'

const STATS = [
  { value: 25, suffix: 'K+', label: 'Agents Audited' },
  { value: 500, suffix: 'K+', label: 'Security Tests' },
  { value: 98, suffix: '%', label: 'Detection Accuracy' },
  { value: 12, suffix: 'M+', label: 'Threat Simulations' },
]

export default function TrustSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section ref={ref} className="py-20 border-y border-white/5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold mb-3">Trusted by Security Teams</h2>
          <p className="text-white/40 max-w-lg mx-auto">Thousands of AI agents tested across enterprises worldwide</p>
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
