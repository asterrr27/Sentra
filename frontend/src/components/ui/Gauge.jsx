import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export default function Gauge({ score = 0, size = 180, label = '' }) {
  const [displayScore, setDisplayScore] = useState(0)
  const radius = 42
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (displayScore / 100) * circumference

  const color = score >= 80 ? '#22C55E' : score >= 50 ? '#F59E0B' : '#EF4444'

  useEffect(() => {
    let raf
    const duration = 1200
    const startTime = performance.now()
    function step(now) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplayScore(Math.round((score) * eased))
      if (progress < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => { if (raf) cancelAnimationFrame(raf) }
  }, [score])

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Radar rings */}
      {[0, 1, 2].map(i => (
        <motion.div
          key={i}
          className="absolute rounded-full border border-primary/10"
          style={{ width: '120%', height: '120%' }}
          animate={{ scale: [0.8, 1.6], opacity: [0.5, 0] }}
          transition={{ duration: 3, repeat: Infinity, delay: i * 1, ease: 'easeOut' }}
        />
      ))}
      <svg className="-rotate-90 relative z-10" width={size} height={size} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
        <motion.circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
          style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
        <span className={`text-3xl font-black tracking-tight ${score >= 80 ? 'text-success' : score >= 50 ? 'text-warning' : 'text-danger'}`}
          style={{ textShadow: `0 0 20px ${color}40` }}>
          {displayScore}
        </span>
        {label && <span className="text-[10px] text-white/40 uppercase tracking-widest mt-1">{label}</span>}
      </div>
    </div>
  )
}
